from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from store.models import Category, Product, ProductImages, Cart, CartItem
from accounts.models import User, Address
from django.core.mail import send_mail
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

# from accounts.forms import UserProfileForm, AddressForm

# Create your views here.

# for the home page 
@never_cache
def home(request):
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

# @never_cache
# def product_detail(request,product_pid):    
#     product = get_object_or_404(Product, p_id=product_pid)
#     product_images = ProductImages.objects.filter(product=product)
#     print(product_images)

#     context = {
#         'product': product,
#         'product_images': product_images,
   
#     }

#     return render(request, 'core/product_detail.html',context)

# for viewing the product details 
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

# for viewing the user details
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


def cart_view(request):
    user_cart = Cart.objects.filter(user=request.user).first()

    if user_cart:
        cart_items = user_cart.items.all()

        for cart_item in cart_items:
            cart_item.total_price = cart_item.product.price * cart_item.quantity
        sub_total = cart_item.total_price
        total_price = sum(cart_item.total_price for cart_item in cart_items)
    else:
        cart_items = []
        total_cart_price = 0

    context = {
          'cart_items': cart_items, 
          'total_price': total_price,
          'sub_total': sub_total,
       }
    return render(request, 'dashboard/user_cart/cart.html', context)


def add_to_cart(request):
    if request.method == 'GET':
        product_pid = request.GET.get('product_pid')
        if product_pid:
            try:
                product = Product.objects.get(pid=product_pid)

                user_cart, created = Cart.objects.get_or_create(user=request.user)
                cart_item, item_created = CartItem.objects.get_or_create(cart=user_cart, product=product)

                if item_created:
                    message = f"{product.title} added to cart"
                else:

                    message = f"{product.title} is already in your cart"

                return JsonResponse({'message': message})
            except Product.DoesNotExist:
                pass


    return HttpResponseBadRequest("Invalid request")


@require_POST
def remove_from_cart(request, cart_item_id):
    
    cart_item = get_object_or_404(CartItem, pk=cart_item_id)
    cart_item.delete()
    return JsonResponse({'message': 'Item removed from cart successfully'}, status=200)