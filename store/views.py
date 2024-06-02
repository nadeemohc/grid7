from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse, HttpResponseNotFound, Http404, HttpResponseServerError, HttpResponseRedirect
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
from django.template.defaultfilters import linebreaksbr
from user_cart.views import checkout
import sweetify



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
    product_attributes = ProductAttribute.objects.all()
    prod_count = Product.objects.count()
    featured_products = Product.objects.filter(featured=True)
    popular_products = Product.objects.filter(popular=True)
    new_added_products = Product.objects.filter(latest=True)
    context = {
        'categories': categories,
        'products': Products,
        'product_attributes': product_attributes,
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
    product_attributes = ProductAttribute.objects.all()

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
        'product_attributes': product_attributes,        
    })
    return render(request, 'dashboard/product_list.html', context)

# for viewing the product details 
def product_detailed_view(request, product_pid):
    # Get the product or return 404 if not found
    product = get_object_or_404(Product, p_id=product_pid)
    
    # Replace newline characters with HTML line break tags
    specifications_lines = product.specifications.split('\n')
    
    # Get product images ordered by upload timestamp
    product_images = ProductImages.objects.filter(product=product).order_by('images')
    
    # Get product attributes including size
    product_attributes = ProductAttribute.objects.filter(product=product)
    title = product.title
    
    context = {
        'product': product,
        'title': title,
        'specifications_lines': specifications_lines,  # Pass the modified specifications to the template
        'product_images': product_images,
        'product_attributes': product_attributes,
    }

    return render(request, 'dashboard/product_detailed_view.html', context)

def get_price(request, size_id):
    try:
        product_attribute = ProductAttribute.objects.get(pk=size_id)
        price = product_attribute.price
        return JsonResponse({'price': price})
    except ProductAttribute.DoesNotExist:
        return JsonResponse({'error': 'Product attribute not found'}, status=404)

# for viewing the user details
@login_required
def user_profile(request):
    user = request.user
    address = Address.objects.filter(user=user)
    orders = CartOrder.objects.filter(user=user).order_by('-id')
    context = {
        'user': user,
        'address':address,
        'orders': orders,
        'title': 'User Profile'
    }

    return render(request, 'dashboard/user_profile.html', context)

def user_order_detail(request, order_id):
    order = get_object_or_404(CartOrder, id=order_id, user=request.user)
    context = {
        'order': order,
    }
    return render(request, 'dashboard/user_order_detail.html', context)

# For adding new address in the user profile
def add_address(request):
    source = request.GET.get('source', None)
    print('Inside addaddress')
    if request.method == 'POST':
        street_address = request.POST.get('street_address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        postal_code = request.POST.get('postal_code')
        country = request.POST.get('country')
        print(street_address, city, state, postal_code, country)
        address = Address.objects.create(
            user = request.user,
            street_address = street_address,
            city = city,
            state = state,
            postal_code = postal_code,
            country = country,
        )
        if source == 'profile_address':
                return redirect('store:user_profile')
        elif source == 'checkout_address':
            return redirect('cart:checkout')
        messages.success(request, """Address Added successfully
                         Check the My Address Tab""")
        # return redirect('store:user_profile')
    
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
    sizes = Size.objects.all()

    prod_count = products.count()
    context = {
        'categories': categories,
        'products': products,
        'sizes': sizes,
        'title': 'Shop',
    }

    return render(request, 'dashboard/shop.html', context)


from django.shortcuts import render
from django.shortcuts import get_object_or_404
from .models import Product, Category

def shop(request, category_id=None):
    # Retrieve all categories
    categories = Category.objects.all()
    product_attributes = ProductAttribute.objects.all()
     
    # Retrieve all products
    products = Product.objects.filter(is_blocked=False)  # Exclude blocked products

    # Filter products by category if category_id is provided
    if category_id:
        products = products.filter(category__pk=category_id)

    # Fetch product images for each product
    # products = Product.objects.all()

    context = {
        'categories': categories,
        'products': products,
        'title': 'Shop',
        'product_attributes': product_attributes,
    }

    return render(request, 'dashboard/shop.html', context)

def order_cancel(request, order_id):
    print('inside cancel')
    order = get_object_or_404(CartOrder, id=order_id)
    order.status = 'Cancelled'
    bv = order.status
    order.save()
    print(bv)
    sweetify.toast(request, 'Order status updated successfully.', timer=3000, icon='success')
    return redirect('store:user_order_detail', order_id = order_id)

def search_products(request):
    query = request.GET.get('search_field', '')
    products = Product.objects.filter(title__icontains=query) if query else Product.objects.none()
    prod_count = products.count()
    categories = Category.objects.filter(is_blocked=False)  # Add this line to fetch categories for the sidebar
    context = {
        'products': products,
        'prod_count': prod_count,
        'categories': categories,
        'category': 'Search Results'  # or any other context you need
    }
    return render(request, 'dashboard/product_search_results.html', context)

def wishlist(request):
    context = {}
    try:
        items = Wishlist.objects.filter(user=request.user).prefetch_related('product__product_attributes')
        context = {
            'items': items,
        }
    except Wishlist.DoesNotExist:
        pass
    return render(request, 'dashboard/wishlist.html', context)

def add_wishlist(request, product_pid):
    if not request.user.is_authenticated:
        messages.info(request, 'Login to access wishlist')
        return redirect('accounts:login')
    else:
        try:
            item = Wishlist.objects.get(user=request.user, product_id=product_pid)
            sweetify.toast(request, 'Product is already in your wishlist', icon='info')
        except Wishlist.DoesNotExist:
            Wishlist.objects.create(user=request.user, product_id=product_pid)
            sweetify.toast(request, 'Product added to your wishlist successfully', icon='success')
        
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

def delete_wishlist(request, pk):
    wishlist = get_object_or_404(Wishlist, id=pk, user=request.user)
    wishlist.delete()
    
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))