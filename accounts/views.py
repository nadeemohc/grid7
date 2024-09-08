import random, sweetify
from accounts.backends import EmailBackend
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import never_cache
from .forms import SignUpForm
from .models import User
from django.contrib.auth import get_user_model
from .models import Wallet, Referral, UserManager
import sweetify
from django.db import IntegrityError


# accounts/views.py
User = get_user_model()
#=========================================== User Signin, login, logout =========================================================================================================

def perform_signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            email = form.cleaned_data.get("email")
            password1 = form.cleaned_data["password1"]
            password2 = form.cleaned_data["password2"]
            phone_number = form.cleaned_data['phone_number']
            first_name = form.cleaned_data.get("first_name")
            last_name = form.cleaned_data.get("last_name")
            entered_referral_code = form.cleaned_data.get("referral_code", "")
            
            # Manually generate a unique referral code for the new user
            referral_code = User.objects.generate_unique_referral_code()

            if password1 != password2:
                sweetify.toast(request, "Entered passwords don't match", icon='info', timer=3000)
                return redirect("accounts:perform_signup")

            if User.objects.filter(email=email).exists():
                sweetify.toast(request, "Email already used!", icon='info', timer=3000)
                return redirect("accounts:perform_signup")

            referrer = None
            if entered_referral_code:
                try:
                    referrer = User.objects.get(referral_code=entered_referral_code)
                except User.DoesNotExist:
                    sweetify.toast(request, "Invalid referral code", icon='error', timer=3000)
                    return redirect("accounts:perform_signup")

            # Create the user with the generated unique referral code
            try:
                user = User.objects.create_user(
                    first_name=first_name,
                    last_name=last_name,
                    username=username,
                    phone_number=phone_number,
                    email=email,
                    password=password1,
                    referral_code=referral_code  # Pass the generated unique referral code
                )
            except IntegrityError as e:
                if 'referral_code' in str(e):
                    sweetify.toast(request, "Duplicate referral code detected, please retry", icon='error', timer=3000)
                else:
                    sweetify.toast(request, "An error occurred during signup", icon='error', timer=3000)
                return redirect("accounts:perform_signup")

            # Update the referrer's wallet and create a referral record
            if referrer:
                referrer.wallet.points += 5
                if referrer.wallet.points >= 10:
                    referrer.wallet.balance += 250
                    referrer.wallet.points -= 10  # Deduct 10 points when balance is credited
                referrer.wallet.save()

                # Add 250 to the new user's wallet
                user.wallet.balance += 250
                user.wallet.save()

                # Create referral record for tracking
                Referral.objects.create(referrer=referrer, referred=user)

            # Store the username in session and send OTP for verification
            request.session["user_id"] = user.username
            sent_otp(request)  # Assumes sent_otp function exists to send OTP

            return render(request, "account/otp.html", {"email": email})
    else:
        form = SignUpForm()

    context = {
        "title": "Signup",
        "form": form,
    }
    return render(request, "account/signup.html", context)


@never_cache
def perform_login(request):
    if request.user.is_authenticated:
        sweetify.toast(request, "You are already logged in", icon='warning', timer=3000)
        return redirect("store:home")

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        # Check if the user exists and is active
        try:
            user = User.objects.get(email=email)
            if not user.is_active:
                sweetify.toast(request, "Access restricted!", icon='warning', timer=3000)
                return redirect("accounts:login")
        except User.DoesNotExist:
            sweetify.toast(request, "User doesn't Exist", icon='warning', timer=3000)
            return redirect("accounts:login")

        # Authenticate the user with the provided credentials
        user = authenticate(request, username=email, password=password)

        if user is not None:
            if user.verified:
                login(request, user)
                request.session["user_logged_in"] = True
                sweetify.toast(request, f"You have logged in as {user.username}", icon='success', timer=3000)
                return redirect("store:home")
            else:
                sweetify.toast(request, "Please verify your account using OTP", icon='error', timer=3000)
                request.session["user_id"] = user.id
                sent_otp(request)
                return redirect("accounts:otp_verification_login")
        else:
            # Failed login attempt
            sweetify.toast(request, "Invalid username or password", icon='warning', timer=3000)
            return redirect("accounts:login")
    context = {
        "title": "Login",
    }
    return render(request, "account/login.html", context)


@never_cache
def perform_logout(request):
    logout(request)
    sweetify.toast(request, "You have logged out", icon='success', timer=3000)
    return redirect("store:home")


#=========================================== Send, resend and verify otp =========================================================================================================


def sent_otp(request):
    otp = "".join([str(random.randint(0, 9)) for _ in range(4)])
    request.session["otp"] = otp

    email = request.POST.get("email")
    subject = "OTP for Sign Up"
    message = f"Your OTP for sign up is {otp}. Please use this code to complete your registration."

    # Specify the connection manually
    connection = get_connection(
        host='smtp.gmail.com',
        port=587,
        username='grid7catalougue@gmail.com',
        password='kjhx kili myhl jtsz',
        use_tls=True,
    )

    # Send the email using the specified connection
    email_message = EmailMessage(subject, message, 'grid7catalougue@gmail.com', [email], connection=connection)
    email_message.send()

    return render(request, "account/otp.html")




def resend_otp(request):
    if request.method == "POST":
        email = request.POST.get("email")
        user = User.objects.filter(email=email).first()
        if user:
            # Generate a new 4-digit OTP
            otp = "".join([str(random.randint(0, 9)) for _ in range(4)])
            request.session["otp"] = otp
            
            # Create the subject and message for the email
            subject = "OTP for Sign Up"
            message = f"Your OTP for sign up is {otp}. Please use this code to complete your registration."

            # Specify the connection manually
            connection = get_connection(
                host='smtp.gmail.com',
                port=587,
                username='grid7catalougue@gmail.com',
                password='kjhx kili myhl jtsz',
                use_tls=True,
            )

            # Send the email using the specified connection
            email_message = EmailMessage(subject, message, 'grid7catalougue@gmail.com', [email], connection=connection)
            email_message.send()

            # Display a success message using SweetAlert
            sweetify.toast(request, "OTP has been resent successfully!", icon='success', timer=3000)
        else:
            # Display an error message if the user doesn't exist
            sweetify.toast(request, "User with this email does not exist!", icon='error', timer=3000)
        
        # Redirect to the OTP verification page
        return redirect("accounts:otp_verification")
    
    # Render the resend OTP page if the request method is not POST
    return render(request, "account/resend_otp.html")


def otp_verification(request):
    if request.method == "POST":
        otp_ = request.POST.get("otp")
        user_id = request.session.get("user_id")
        print('inside verify')

        if otp_ == request.session.get("otp"):
            user = User.objects.get(username=user_id)
            print('user id and name', user, user_id)
            user.verified = True
            user.save()
            request.session.flush()  # Clear the session after verification

            sweetify.toast(request, "OTP verified successfully.", icon='success', timer=3000)

            # Authenticate the user
            user = authenticate(request, username=user.username, password=user.password)

            if user is not None:
                # Log in the user
                login(request, user)
                return redirect("store:home")
            else:
                return redirect("accounts:login")
        else:
            sweetify.toast(request, "Invalid OTP. Please try again.", icon='error', timer=3000)
            return redirect("accounts:otp_verification")

    # If it's a GET request, you don't need the `user` context unless you're using it in the template
    return render(request, "account/otp.html")


def otp_verification_login(request):
    if request.method == "POST":
        otp_ = request.POST.get("otp")
        user_id = request.session.get("user_id")
        user = User.objects.all()

        if otp_ == request.session["otp"]:
            user = User.objects.get(id=user_id)
            user.verified = True
            user.save()
            request.session.flush()
            sweetify.toast(request, "OTP verified successfully.", icon='success', timer=3000)

            # Authenticate the user
            user = authenticate(request, user=user)

            if user is not None:
                # Log in the user
                login(request, user)
                return redirect("store:home")
            else:
                return redirect("accounts:login")  # Redirect to login page or any other appropriate URL
        else:
            sweetify.toast(request, "Invalid OTP. Please try again.", icon='error', timer=3000)
            return redirect("accounts:otp_verification")
    else:
        return render(request, "account/otp1.html")

