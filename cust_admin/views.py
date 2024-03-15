from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from accounts.models import User
from store.models import Category, Product
from django.contrib import messages

def dashboard(request):
    return render(request, 'cust_admin/index.html', {'title':'Admin Dashboard'})

def user_list(request):
    users = User.objects.all().order_by('id')
    return render(request, 'cust_admin/user/user_list.html', {'title':'User List', 'users': users})

def user_view(request, username):
    user = get_object_or_404(User, username=username)
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

def category_list(request):
    categories = Category.objects.all().order_by('c_id')
    return render(request, 'cust_admin/category/category_list.html', {'title':'Category List','categories':categories})

def add_category(request):
    if request.method == 'POST':
        c_name = request.POST.get('cname')
        c_image = request.FILES.get('image')
        # is_blocked = request.POST.get('blocked')
        c_data = Category(c_name = c_name, c_image = c_image)
        c_data.save()
        return redirect('cust_admin:category_list')
          
    return render(request, 'cust_admin/category/add_category.html', {'title':'Add Category'})

def category_list_unlist(request, c_id):
    category = get_object_or_404(Category, c_id = c_id)
    category.is_blocked = not category.is_blocked
    category.save()
    action = 'unblocked' if not category.is_blocked else 'blocked'
    messages.success(request, f"The category with ID {category.c_id} has been {action} successfully.")
    return redirect('cust_admin:category_list')

def add_sub(request):
    return render(request, 'cust_admin/category/add_sub_cat.html')

# def product_list(request):

#     products = Product.objects.all()

#     return render(request,'appadmin/product/admin_product_list.html',{'title':'Product List', 'products':products})

def prod_list(request):
    products = Product.objects.all()
    return render(request, 'cust_admin/product/product_list.html', {'title':'Product List', 'products':products})