from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from accounts.models import User

def dashboard(request):
    return render(request, 'cust_admin/index.html', {'title':'Admin Dashboard'})

def user_list(request):
    users = User.objects.all()
    return render(request, 'cust_admin/user_list.html', {'title':'User List', 'users': users})

def admin_view_user(request, username):
    user = get_object_or_404(User, username=username)
    return render(request, 'cust_admin/view_user.html', {'title': 'View User', 'user': user})

User = get_user_model()
