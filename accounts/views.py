from django.shortcuts import render, redirect
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
            encryptedpassword = make_password(form.cleaned_data.get('password1'))
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')

            print(username, email, encryptedpassword, first_name, last_name)
            user = User.objects.create(username= username,
                                           email = email,
                                           password = encryptedpassword,
                                           first_name = first_name,
                                           last_name = last_name)
                                        #    verified = False)


            request.session["user_id"] = user.id

            sent_otp(request)
            return render(request,'account/otp.html',{"email":email})

          
        
    else: 
        form = SignUpForm()
    context = {
        'form':form
        }
    return render(request,'account/signup.html',context)


@never_cache
def perform_login(request):
    if request.user.is_authenticated:
        messages.warning(request, 'You are already logged in')
        return redirect("store:home")
    
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        print(email, password)
        user = authenticate(request, username=email, password=password)
        # user=User.objects.get(email=email)
        print(user)
        if user is not None:
            login(request, user)
            request.session['user_logged_in'] = True
            messages.success(request, 'You have logged in')
            return redirect('store:home')
        else:
            messages.warning(request, 'Incorrect email or password')
    return render(request, 'account/login.html')





def sent_otp(request):
    s = ''
    for x in range(0, 4):
        s += str(random.randint(0, 9))
    request.session["otp"] = s
    email = request.POST.get('email') 
    send_mail("otp for sign up", s, "mn8697865@gmail.com", [email], fail_silently=False)
    return render(request, 'account/otp.html')


def otp_verification(request):
    if request.method=='POST':
        otp_=request.POST.get("otp")
        user_id = request.session.get('user_id')

        if otp_ == request.session["otp"]:
            user = User.objects.get(id=user_id)
            user.verified = True
            user.save()
            request.session.flush()
            messages.success(request, "OTP verified successfully.")
            return redirect('store:home')  
        else:
            messages.error(request, "Invalid OTP. Please try again.")
            return redirect('otp_verification')  
    else:
        return render(request, 'account/otp.html')




def perform_logout(request):
    logout(request)
    messages.success(request, 'You have logged out')
    return redirect('store:home')