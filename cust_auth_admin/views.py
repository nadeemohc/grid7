from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from cust_admin import views
from django.contrib.auth.decorators import user_passes_test
from accounts.models import User
from django.contrib.auth import login, logout, authenticate
import sweetify


#=========================================== custom decorator to check if the user is admin ===========================================================================================


def is_admin(user):
    return user.is_authenticated and user.is_superadmin


def admin_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not is_admin(request.user):
            # Redirect the user to a login page or display an error message
            return redirect('admin_auth:admin_login')  # Adjust the URL name as per your project
        return view_func(request, *args, **kwargs)
    return _wrapped_view


#=========================================== login, logout for admin ======================================================================================================================


def admin_login(request):
    if request.user.is_authenticated and request.user.is_superadmin:
        return redirect('cust_admin:admin_dashboard')
    
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, email=email, password=password)
        
        if user is not None:
            if user.is_superadmin:
                login(request, user)
                # Add the welcome message here
                sweetify.toast(request, f'Welcome, {user.first_name}!', icon='success', timer=3000)
                return redirect('cust_admin:admin_dashboard')
            else:
                sweetify.toast(request, 'Invalid admin credentials', icon='error', timer=3000)
        else:
            sweetify.toast(request, 'Invalid email or password', icon='error', timer=3000)
            
    return render(request, 'cust_admin/admin_login.html', {'title':'Admin Login'})

    
@admin_required
def admin_logout(request):
    logout(request)
    messages.success(request, 'You have logged out')
    return redirect('admin_auth:admin_login')