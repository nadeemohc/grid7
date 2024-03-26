from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import SignUpForm
from accounts.backends import EmailBackend
from django.contrib.auth import authenticate, login, logout
from .models import User
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.views.decorators.cache import never_cache
import random

def perform_signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            phone_number = request.POST.get('phone_number')
            password1 = form.cleaned_data['password1']
            password2 = form.cleaned_data['password2']
            encryptedpassword = make_password(form.cleaned_data.get('password1'))
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')

            try:
                user_with_email = User.objects.get(email=email)
                messages.info(request, 'Email already used!')
                return redirect('accounts:perform_signup')
            except User.DoesNotExist:
                pass  # Email is not in use, continue with registration

            if password1 != password2:
                messages.info(request, "Entered passwords don't match")
                return redirect('accounts:perform_signup')

            user = User.objects.create(username=username,
                                       email=email,
                                       phone_number=phone_number,
                                       password=encryptedpassword,
                                       first_name=first_name,
                                       last_name=last_name)

            request.session["user_id"] = user.id
            sent_otp(request)
            return render(request, 'account/otp.html', {"email": email})

    else: 
        form = SignUpForm()

    context = {'form': form}
    return render(request, 'account/signup.html', context)


@never_cache
def perform_login(request):
    if request.user.is_authenticated:
        messages.warning(request, 'You are already logged in')
        return redirect("store:home")
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Check if the user exists and is active
        try:
            user = User.objects.get(email=email)
            if not user.is_active:
                messages.warning(request, "Access restricted!")
                return redirect('accounts:login')
        except User.DoesNotExist:
            messages.warning(request, 'Incorrect email or password')
            return redirect('accounts:login')
        
        # Authenticate the user with the provided credentials
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            if user.verified:
                login(request, user)
                request.session['user_logged_in'] = True
                messages.success(request, f'You have logged in as {user.username}')
                return redirect('store:home')
            else:
                messages.error(request, 'Please verify your account using OTP')
                request.session["user_id"] = user.id
                sent_otp(request)
                return redirect('accounts:otp_verification')
        
    return render(request, 'account/login.html')



def edit_info(request):
    user = get_object_or_404(User, )
    return render(request, 'dashboard/edit_profile.html')


def sent_otp(request):
    s = ''
    for x in range(0, 4):
        s += str(random.randint(0, 9))
    request.session["otp"] = s
    email = request.POST.get('email') 
    send_mail("otp for sign up", s, "mn8697865@gmail.com", [email], fail_silently=False)
    return render(request, 'account/otp.html')

def resend_otp(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = User.objects.filter(email=email).first()
        if user:
            send_mail("otp for sign up", s, "mn8697865@gmail.com", [email], fail_silently=False)
            messages.success(request, 'OTP has been resent successfully!')
        else:
            messages.error(request, 'User with this email does not exist!')
        return redirect('account:otp_verification')  # Redirect to the OTP verification page
    return render(request, 'account/resend_otp.html')

# def otp_verification(request):
#     if request.method=='POST':
#         otp_=request.POST.get("otp")
#         user_id = request.session.get('user_id')

#         if otp_ == request.session["otp"]:
#             user = User.objects.get(id=user_id)
#             user.verified = True
#             user.save()
#             request.session.flush()
#             messages.success(request, "OTP verified successfully.")
#             login(request, user)
#             return redirect('store:home')  
#         else:
#             messages.error(request, "Invalid OTP. Please try again.")
#             return redirect('otp_verification')  
#     else:
#         return render(request, 'account/otp.html')



def otp_verification(request):
    if request.method == 'POST':
        otp_ = request.POST.get("otp")
        user_id = request.session.get('user_id')

        if otp_ == request.session["otp"]:
            user = User.objects.get(id=user_id)
            user.verified = True
            user.save()
            request.session.flush()
            messages.success(request, "OTP verified successfully.")
            
            # Authenticate the user
            user = authenticate(request, user=user)
            
            if user is not None:
                # Log in the user
                login(request, user)
                return redirect('store:home')
            else:
                # messages.error(request, "Failed to log in. Please try again.")
                return redirect('accounts:login')  # Redirect to login page or any other appropriate URL
        else:
            messages.error(request, "Invalid OTP. Please try again.")
            return redirect('otp_verification')  
    else:
        return render(request, 'account/otp.html')

@never_cache
def perform_logout(request):
    logout(request)
    messages.success(request, 'You have logged out')
    return redirect('store:home')
