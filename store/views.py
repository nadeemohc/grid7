from django.shortcuts import render, redirect
from store.models import Category, Product, ProductImages
from accounts.models import User, Address
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.views.decorators.cache import never_cache
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
# from accounts.forms import UserProfileForm, AddressForm

# Create your views here.

@never_cache
def home(request):
    categories = Category.objects.all()
    Products = Product.objects.all()
    # featured_products = Product.objects.filter(featured=True)
    # popular_products = Product.objects.filter(popular=True)
    # new_added_products = Product.objects.filter(latest=True)
    return render(request, 'dashboard/home.html', 
                  {'title':'Home',
                   'categories':categories,
                   'products':Products})


def handler404(request, exception):
    return render(request, '404.html', status=404)

@never_cache
def product_detail(request,product_pid):    
    product = get_object_or_404(Product, p_id=product_pid)
    product_images = ProductImages.objects.filter(product=product)
    print(product_images)

    context = {
        'product': product,
        'product_images': product_images,
   
    }

    return render(request, 'core/product_detail.html',context)


def product_detailed_view(request,product_pid):
    product = get_object_or_404(Product, p_id=product_pid)
    product_images = ProductImages.objects.filter(product=product)
    print(product_images)

    context = {
        'product': product,
        'product_images': product_images,
        'breadcrumb': product.title,
   
    }

    return render(request, 'dashboard/product_detailed_view.html',context)


def user_profile(request):
    User = request.user
    address = Address.objects.all()
    return render(request, 'dashboard/user_profile.html', {'title':'User Profile','user':User, 'address':address})


def add_address(request):
    
    if request.method == 'POST':
        street_address = request.POST.get('street_address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        postal_code = request.POST.get('postal_code')
        country = request.POST.get('country')
        
        address = Address.objects.create(
            user = request.user,
            street_address = street_address,
            city = city,
            state = state,
            postal_code = postal_code,
            country = country,
        )
        print(address)
        messages.success(request, """Address Added successfully
                         Check the My Address Tab""")
        return redirect('store:user_profile')
    
    return render(request, 'dashboard/user_profil.html',{'address': address})





@login_required
def edit_profile(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        user = request.user

        user.first_name = first_name
        user.last_name = last_name
        user.username = username
        user.email = email
        user.phone_number = phone_number
        user.save()

        messages.success(request, "Profile Updated Successfully")
        return redirect('store:user_profile')

    return render(request, 'dashboard/user_profile.html', {'title':'User Profile','user':User})


def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important to maintain the user's session
            messages.success(request, 'Your password was successfully updated!')
            return redirect('store:user_profile')  # Redirect to a success page
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'dashboard/change_password.html', {'form': form})
