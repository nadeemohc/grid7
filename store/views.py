from django.http import HttpResponseBadRequest, JsonResponse, HttpResponseNotFound
from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from accounts.models import User, Address
from django.db.models import Sum
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
    products = ProductAttribute.objects.all()
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
from django.http import Http404

from django.http import HttpResponseServerError
from django.template.defaultfilters import linebreaksbr

from django.http import HttpResponseServerError
from django.http import HttpResponse, HttpResponseServerError
from django.shortcuts import render
from django.db.models import Sum

def product_detailed_view(request, product_pid):
    try:
        # Get all product attributes with the given product_pid
        product_attributes = ProductAttribute.objects.filter(product__p_id=product_pid)
        
        # Check if product attributes exist
        if product_attributes.exists():
            # Get the corresponding product instance (assuming product is the same for all variants)
            product = product_attributes.first().product

            # Get the product images associated with the product
            product_images = ProductImages.objects.filter(product=product)
            
            # Define the custom ordering for sizes
            custom_order = {'S': 0, 'M': 1, 'L': 2, 'XL': 3, 'XXL': 4, 'XXXL': 5}
            
            # Get the size options for the product and order them based on the custom ordering
            sizes = product_attributes.values_list('size__size', flat=True).distinct()
            sizes = sorted(sizes, key=lambda x: custom_order.get(x, 999))
            
            sub = Product.objects.all()
            
            # Count of total products
            product_count = product_attributes.aggregate(total_stock=Sum('stock'))['total_stock']
            
            # Get the product specifications and split by newline characters
            ps_lines = product.specifications.split('\n') if product.specifications else []
            
            context = {
                'product': product,
                'product_id': product_pid,
                'sub': sub,
                'product_attributes': product_attributes,
                'product_count': product_count,
                'product_images': product_images,
                'sizes': sizes,
                'breadcrumb2': product.category,
                'breadcrumb3': product.title,
                'ps_lines': ps_lines,  # Pass the list of specification lines to the template
            }
            
            # Return the rendered template with the context
            return render(request, 'dashboard/product_detailed_view.html', context)
        else:
            # Return an error message if product attributes do not exist
            return HttpResponseServerError('Product attributes not found')

    except Exception as e:
        # Log the exception
        print("Error fetching product:", e)
        # Return an appropriate response
        return HttpResponseServerError('Error fetching product')

    


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


from django.shortcuts import render
from django.shortcuts import get_object_or_404
from .models import Product, ProductImages, Category

def shop(request, category_id=None):
    categories = Category.objects.all()
    products = Product.objects.all()

    if category_id:
        category = get_object_or_404(Category, pk=category_id)
        products = products.filter(category=category)
    
    # Fetch product images for each product
    product_images = {}
    for product in products:
        images = ProductImages.objects.filter(product=product)
        product_images[product.pk] = images.first() if images.exists() else None
    
    context = {
        'categories': categories,
        'products': products,
        'title': 'Shop',
        'product_images': product_images,  # Pass product images to the template
    }

    return render(request, 'dashboard/shop.html', context)


# def shop(request, category_id=None):
#     categories = Category.objects.all()
#     prod = ProductAttribute.objects.all()
#     products = Product.objects.all()
#     featured_products = prod.filter(featured=True)
#     popular_products = prod.filter(popular=True)
#     new_added_products = prod.filter(latest=True)

#     if category_id:
#         category = get_object_or_404(Category, pk=category_id)
#         products = Product.objects.filter(category=category)
#     else:
#         products = Product.objects.all()
    
#     prod_count = products.count()
    
#     context = {
#         'categories': categories,
#         'products': products,
#         'prod': prod,
#         'featured_products': featured_products,
#         'new_added_products': new_added_products,
#         'popular_products': popular_products,
#         'title': 'Shop',
#         'prod_count': prod_count,  # Add this if you want to display product count
#     }

#     return render(request, 'dashboard/shop.html', context)