from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from accounts.models import User
from django.contrib import messages

def dashboard(request):
    return render(request, 'cust_admin/index.html', {'title':'Admin Dashboard'})

def user_list(request):
    users = User.objects.all().order_by('id')
    return render(request, 'cust_admin/user/user_list.html', {'title':'User List', 'users': users})

def user_view(request, username):
    user = get_object_or_404(User, username=username)
    # context = {
    #     'user
    # }
    return render(request, 'cust_admin/user/user_view.html', {'title': 'View User', 'user': user})

User = get_user_model()


def user_block_unblock(request, username):
    user = get_object_or_404(User, username = username)
    user.is_active = not user.is_active
    user.save()
    action = 'blocked' if not user.is_active else 'unblocked'
    messages.success(request, f"The user {user.username} has been {action} successfully.")
    return redirect('cust_admin:user_list')

def add_product(request):
    return render(request, 'cust_admin/product/product_add.html', {'title':'Add Product'})

def prod_list(request):
    return render(request, 'cust_admin/product/product_list.html', {'title':'Product List'})

def category_list(request):
    return render(request, 'cust_admin/category/category_list.html', {'title':'Category List'})