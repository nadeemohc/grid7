from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from store.models import Category, Product, ProductImages, Size
from accounts.models import User, Address
from django.core.mail import send_mail
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

# for the home page 
def get_common_context():
    return {
        'categories': Category.objects.filter(is_blocked=False),
    }
@never_cache
def home(request):
    categories = Category.objects.all()
    products = Product.objects.all()
    prod_count = products.count()
    featured_products = products.filter(featured=True)
    popular_products = products.filter(popular=True)
    new_added_products = products.filter(latest=True)
    context = {
        'categories': categories,
        'products': products,
        'prod_count': prod_count,
        'featured_products': featured_products,
        'new_added_products': new_added_products,
        'popular_products': popular_products,
        'title': 'Home',
    }
    return render(request, 'dashboard/home.html', context)

# For displaying the 404 page
def handler404(request, exception):
    return render(request, '404.html', status=404)

# For listing the products in shop page
def list_prod(request):
    categories = Category.objects.all()
    Products = Product.objects.all()
    prod_count = Product.objects.count()
    featured_products = Product.objects.filter(featured=True)
    popular_products = Product.objects.filter(popular=True)
    new_added_products = Product.objects.filter(latest=True)
    context = {
        'categories': categories,
        'products': Products,
        'prod_count': prod_count,
        'featured_products': featured_products,
        'new_added_products':new_added_products,
        'popular_products': popular_products,
        'title': 'Shop',
    }
    return render(request, 'dashboard/shop.html', context)

def product_list_by_category(request, category_cid):
    category = get_object_or_404(Category, c_id=category_cid)
    products = Product.objects.filter(category=category)
    prod_count = products.count()
    

    if request.method == 'POST':
            
            price_range = request.POST.get('price_range')
            
            if price_range:
                if price_range == '0-50':
                    products = products.filter(price__range=(0, 50))
                elif price_range == '50-200':
                    products = products.filter(price__range=(50, 200))
                elif price_range == '200-500':
                    products = products.filter(price__range=(200, 500))
                elif price_range == '500-1000':
                    products = products.filter(price__range=(500, 1000))
                elif price_range == 'more than 1000':
                    products = products.filter(price__gt=1000)

    context = get_common_context()
    context.update({
        'category': category,
        'products': products,
        'prod_count': prod_count,
        
    })
    return render(request, 'dashboard/product_list.html', context)

# for viewing the product details 
def product_detailed_view(request, product_pid):
    product = get_object_or_404(Product, p_id=product_pid)
    product_images = ProductImages.objects.filter(product=product)
    
    # Get the size options for the product
    sizes = product.size.all()
    product_count = Product.objects.count()

    context = {
        'product': product,
        'product_count': product_count,
        'product_images': product_images,
        'sizes': sizes,  # Pass the sizes to the template
        'breadcrumb': product.title,
    }

    return render(request, 'dashboard/product_detailed_view.html', context)


# for viewing the user details
@login_required
def user_profile(request):
    user = request.user
    address = Address.objects.filter(user=user)
    return render(request, 'dashboard/user_profile.html', {'title': 'User Profile', 'user': user, 'address': address})

# For adding new address in the user profile
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
        messages.success(request, """Address Added successfully
                         Check the My Address Tab""")
        return redirect('store:user_profile')
    
    return render(request, 'dashboard/user_profil.html',{'address': address})

# for editing the address
@login_required
def edit_address(request, address_id):
    address = get_object_or_404(Address, id=address_id)
    
    if request.method == 'POST':
        address.street_address = request.POST.get('street_address')
        address.city = request.POST.get('city')
        address.state = request.POST.get('state')
        address.postal_code = request.POST.get('postal_code')
        address.country = request.POST.get('country')
        address.save()
        
        messages.success(request, "Address updated successfully")
        return redirect('store:user_profile')
    
    return render(request, 'dashboard/user_profile.html', {'address': address})


# for deleting the existing address
def delete_address(request, pk):
    address = get_object_or_404(Address, pk=pk)
    # Check if the logged-in user is the owner of the address
    if request.user == address.user:
        address.delete()
    return redirect('store:user_profile')

# for editing the existing user details
# url name: store:edit_profile
@login_required
def edit_profile(request):
    if request.method == 'POST':
        # Retrieve user details from the request
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        user = request.user

        # Update user details
        user.first_name = first_name
        user.last_name = last_name
        user.username = username
        user.email = email
        user.phone_number = phone_number
        user.save()

        # Send email to the user
        subject = 'Profile Updated'
        message = 'Your profile has been successfully updated.'
        send_mail(subject, message, None, [user.email])

        # Redirect to user profile page
        messages.success(request, "Profile Updated Successfully")
        return redirect('store:user_profile')

    return render(request, 'dashboard/user_profile.html', {'title':'User Profile','user':request.user})

# for changing the password of the logged in user
# url name: store:change_password
@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            # Send email verification
            send_email_verification(request.user.email)
            return redirect('accounts:logout')  # Redirect to a success page
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'dashboard/change_password.html', {'form': form})

# for sending the email saying password has changed(store:change_password)
def send_email_verification(email):
    subject = 'Password Change Verification'
    message = 'Your password has been successfully changed. If you did not make this change, please contact us immediately.'
    from_email = 'mn8697865@gmail.com'  # Use your email
    recipient_list = [email]
    send_mail(subject, message, from_email, recipient_list)


def shop(request):
    categories = Category.objects.all()
    products = Product.objects.all()
    prod_count = products.count()
    context = {
        'categories': categories,
        'products': products,
        'title': 'Shop',
    }

    return render(request, 'dashboard/shop.html', context)


def shop(request, category_id=None):
    categories = Category.objects.all()
    products = Product.objects.all()
    featured_products = products.filter(featured=True)
    popular_products = products.filter(popular=True)
    new_added_products = products.filter(latest=True)

    if category_id:
        category = get_object_or_404(Category, pk=category_id)
        products = Product.objects.filter(category=category)
    else:
        products = Product.objects.all()
    
    prod_count = products.count()
    
    context = {
        'categories': categories,
        'products': products,
        'featured_products': featured_products,
        'new_added_products': new_added_products,
        'popular_products': popular_products,
        'title': 'Shop',
        'prod_count': prod_count,  # Add this if you want to display product count
    }

    return render(request, 'dashboard/shop.html', context)
