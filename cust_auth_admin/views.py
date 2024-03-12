from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from accounts.models import User
from django.contrib.auth import login, logout, authenticate


# Create your views here.

def admin_login(request):
    if request.user.is_authenticated and request.user.is_superuser:
        return redirect('cust_admin:dashboard')
    else:
        return render(request, 'cust_admin/admin_login.html', {'title':'Admin Login'})
    
def admin_logout(request):
    logout(request)
    messages.success(request, 'You have logged out')
    return redirect('admin_auth:admin_login')