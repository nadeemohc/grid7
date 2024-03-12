from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from cust_admin import views
from accounts.models import User
from django.contrib.auth import login, logout, authenticate


# Create your views here.

def admin_login(request):
    if request.user.is_authenticated and request.user.is_superadmin:
        return redirect('cust_admin:admin_dashboard')
    
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        print(email,password)
        user = authenticate(request, email = email, password = password)
        if user:
            if user.is_superadmin:
                login(request, user)
                return redirect('cust_admin:admin_dashboard')
            
            messages.error(request, 'Invalid admin credentials')
    return render(request, 'cust_admin/admin_login.html', {'title':'Admin Login'})
    
def admin_logout(request):
    logout(request)
    messages.success(request, 'You have logged out')
    return redirect('admin_auth:admin_login')