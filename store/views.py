from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse, HttpResponseNotFound, Http404, HttpResponseServerError, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from .models import Coupon
from decimal import Decimal
from accounts.models import User, Address
from django.db.models import Sum, Min, Max
from django.core.mail import send_mail
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.template.defaultfilters import linebreaksbr
from user_cart.views import checkout
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
import sweetify
from django.conf import settings
from django.utils import timezone
from django.db.models import F, ExpressionWrapper, DecimalField


def get_common_context():
    return {
        'categories': Category.objects.filter(is_blocked=False),
    }


#=============================================================================== Home =============================================================================================


@never_cache
def home(request):
    categories = Category.objects.all()
    products = Product.objects.all()
    prod_count = products.count()
    featured_products = products.filter(featured=True)
    popular_products = products.filter(popular=True)
    new_added_products = products.filter(latest=True)
    
    # Get the 'Poster' subcategory
    poster_subcategory = Subcategory.objects.filter(sub_name='Posters').first()
    
    # Filter products by the 'Poster' subcategory
    poster_products = products.filter(sub_category=poster_subcategory) if poster_subcategory else Product.objects.none()
    print(poster_products,'poster')
    # Apply offers
    featured_products = [apply_offers(p) for p in featured_products]
    popular_products = [apply_offers(p) for p in popular_products]
    new_added_products = [apply_offers(p) for p in new_added_products]
    poster_products = [apply_offers(p) for p in poster_products]

    context = {
        'categories': categories,
        'products': products,
        'prod_count': prod_count,
        'featured_products': featured_products,
        'new_added_products': new_added_products,
        'popular_products': popular_products,
        'poster_products': poster_products,  # Add this to the context
        'title': 'Home',
    }
    return render(request, 'dashboard/home.html', context)


def handler404(request, exception):
    return render(request, '404.html', status=404)


#========================================================================== views related to product =========================================================================================


def list_prod(request):
    categories = Category.objects.all()
    products = Product.objects.all()
    product_attributes = ProductAttribute.objects.all()
    prod_count = Product.objects.count()
    featured_products = Product.objects.filter(featured=True)
    popular_products = Product.objects.filter(popular=True)
    new_added_products = Product.objects.filter(latest=True)

    featured_products = [apply_offers(p) for p in featured_products]
    popular_products = [apply_offers(p) for p in popular_products]
    new_added_products = [apply_offers(p) for p in new_added_products]

    context = {
        'categories': categories,
        'products': products,
        'product_attributes': product_attributes,
        'prod_count': prod_count,
        'featured_products': featured_products,
        'new_added_products': new_added_products,
        'popular_products': popular_products,
        'title': 'Shop',
    }
    return render(request, 'dashboard/shop.html', context)


def product_list_by_category(request, category_cid):
    category = get_object_or_404(Category, c_id=category_cid)
    search_field = request.GET.get('search_field', '')
    products = Product.objects.filter(category=category, is_blocked=False)

    if search_field:
        products = products.filter(title__icontains=search_field)

    products = [apply_offers(p) for p in products]

    price_filter = request.GET.get('price_filter')
    if price_filter:
        if price_filter == 'below_500':
            products = [p for p in products if p.final_price < 500]
        elif price_filter == '500_1000':
            products = [p for p in products if 500 <= p.final_price < 1000]
        elif price_filter == '1000_1500':
            products = [p for p in products if 1000 <= p.final_price < 1500]
        elif price_filter == '1500_2000':
            products = [p for p in products if 1500 <= p.final_price < 2000]
        elif price_filter == 'above_2000':
            products = [p for p in products if p.final_price >= 2000]

    # Sort by
    sort_by = request.GET.get('sort_by')
    if sort_by:
        if sort_by == 'price_asc':
            products = sorted(products, key=lambda p: p.final_price)
        elif sort_by == 'price_desc':
            products = sorted(products, key=lambda p: p.final_price, reverse=True)
        elif sort_by == 'name_asc':
            products = sorted(products, key=lambda p: p.title)
        elif sort_by == 'name_desc':
            products = sorted(products, key=lambda p: p.title, reverse=True)
        # elif sort_by == 'new_arrivals':
        #     products = sorted(products, key=lambda p: p.updated, reverse=True)
        elif sort_by == 'avg_rating':
            products = sorted(products, key=lambda p: p.avg_rating, reverse=True)

    items_per_page = request.GET.get('items_per_page', 9)
    paginator = Paginator(products, items_per_page)
    page = request.GET.get('page')

    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    context = {
        'category': category,
        'products': page_obj,
        'categories': Category.objects.all(),
        'prod_count': paginator.count,
        'items_per_page': items_per_page,
        'price_filter': price_filter,
        'page_obj': page_obj,
        'search_field': search_field,
        'sort_by': sort_by,
    }
    return render(request, 'dashboard/product_list.html', context)


def product_detailed_view(request, product_pid):
    product = get_object_or_404(Product, p_id=product_pid)
    specifications_lines = product.specifications.split('\n')
    product_images = ProductImages.objects.filter(product=product).order_by('images')
    product_attributes = ProductAttribute.objects.filter(product=product)
    title = product.title

    # Apply offers to the product
    product = apply_offers(product)

    # Sort the product_attributes based on price
    sorted_product_attributes = sorted(product_attributes, key=lambda attr: attr.price)

    context = {
        'product': product,
        'title': title,
        'specifications_lines': specifications_lines,
        'product_images': product_images,
        'product_attributes': sorted_product_attributes,
    }
    return render(request, 'dashboard/product_detailed_view.html', context)


def get_price(request, size_id):
    try:
        product_attribute = ProductAttribute.objects.get(pk=size_id)
        price = product_attribute.price
        return JsonResponse({'price': price})
    except ProductAttribute.DoesNotExist:
        return JsonResponse({'error': 'Product attribute not found'}, status=404)


#=========================================== views related to user profile =================================================================================================================================


@login_required
def user_profile(request):
    user = request.user
    address = Address.objects.filter(user=user)
    orders = CartOrder.objects.filter(user=user).order_by('-id')
    wallet = Wallet.objects.filter(user=user).first()  # Get the user's wallet
    wal_history = WalletHistory.objects.filter(wallet=wallet) if wallet else []  # Filter wallet history based on the user's wallet
    item = ProductOrder.objects.filter(user=user)
    referral_code = user.referral_code  # Assuming referral_code is in the User model
    coupons = Coupon.objects.all()
    print(user.phone_number)
    
    context = {
        'user': user,
        'item': item,
        'referral_code': referral_code,
        'wal_history': wal_history,
        'address': address,
        'orders': orders,
        'title': 'User Profile',
        'wallet': wallet,
        'coupons': coupons
    }

    return render(request, 'dashboard/user_profile.html', context)


@login_required
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


@login_required
def delete_address(request, pk):
    address = get_object_or_404(Address, pk=pk)
    # Check if the logged-in user is the owner of the address
    if request.user == address.user:
        address.delete()
    return redirect('store:user_profile')


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


def send_email_verification(email):
    subject = 'Password Change Verification'
    message = 'Your password has been successfully changed. If you did not make this change, please contact us immediately.'
    from_email = 'mn8697865@gmail.com'  # Use your email
    recipient_list = [email]
    send_mail(subject, message, from_email, recipient_list)


@login_required
def user_order_detail(request, order_id):
    order = get_object_or_404(CartOrder, id=order_id, user=request.user)
    context = {
        'order': order,
    }
    return render(request, 'dashboard/user_order_detail.html', context)


@login_required
def order_cancel(request, order_id):
    order = get_object_or_404(CartOrder, id=order_id, user=request.user)
    if order.status != 'Cancelled':
        if order.payment_method == 'Razorpay' or order.payment_method == 'Wallet' or order.payment_method == 'Wallet-Razorpay':
            # Logic for Razorpay refund to wallet
            wallet, created = Wallet.objects.get_or_create(user=request.user)
            wallet.balance += Decimal(order.order_total)
            wallet.save()
            WalletHistory.objects.create(
                wallet=wallet,
                transaction_type='Credit',
                amount=order.order_total,
                reason='Order Cancellation'
            )
        order.status = 'Cancelled'
        order.save()
        sweetify.toast(request, 'Your order has been cancelled and amount refunded to your wallet.',icon='success', timer=3000)
    else:
        sweetify.toast(request, 'Your order is already cancelled.',icon='warning', timer=3000)
    return redirect('store:user_order_detail', order_id=order.id)


@login_required
def order_return(request, order_id):
    order = get_object_or_404(CartOrder, id=order_id, user=request.user)

    if request.method == 'POST':
        sizing_issues = 'sizing_issues' in request.POST
        damaged_item = 'damaged_item' in request.POST
        incorrect_order = 'incorrect_order' in request.POST
        delivery_delays = 'delivery_delays' in request.POST
        customer_service = 'customer_service' in request.POST
        other_reason = request.POST.get('description', '')

        if order.status == 'Delivered':
            print('order = ', order)
            # Save the return request for admin review
            ReturnReason.objects.create(
                user=request.user,
                order=order,
                sizing_issues=sizing_issues,
                damaged_item=damaged_item,
                incorrect_order=incorrect_order,
                delivery_delays=delivery_delays,
                customer_service=customer_service,
                other_reason=other_reason
            )
            order.status = 'Return Requested'
            order.save()
            sweetify.toast(request, 'Your return request has been submitted for review.', icon='success', timer=3000)
        else:
            sweetify.toast(request, 'Your order is not eligible for return.', icon='warning', timer=3000)

        return redirect('store:user_order_detail', order_id=order.id)

    return render(request, 'store/order_return.html', {'order': order})


#=========================================== views related to filter, coupon, offers =================================================================================================================================


def apply_offers(product):
    product_attributes = ProductAttribute.objects.filter(product=product)
    if not product_attributes.exists():
        return product

    product_attribute = product_attributes.first()  # Adjust logic if necessary to handle multiple attributes

    product_offer = ProductOffer.objects.filter(product=product).first()
    category_offer = CategoryOffer.objects.filter(category=product.category).first()

    if product_offer and product_offer.is_active():
        discount = product_offer.discount_percentage
        product.final_price = product_attribute.price - (product_attribute.price * discount / 100)
        print(product.title,product.final_price)
    elif category_offer and category_offer.is_active():
        discount = category_offer.discount_percentage
        product.final_price = product_attribute.price - (product_attribute.price * discount / 100)
    else:
        product.final_price = product_attribute.price

    return product


def list_coupon(request):
    print("inside coupons")
    today = timezone.now().date()
    coupons = Coupon.objects.all()
    # coupons = Coupon.objects.filter(active=True, active_date__lte=today, expiry_date__gte=today)
    return render(request, 'dashboard/user_profile.html', {'coupons': coupons})
    

def filter_product(request):
    try:
        # Get the min and max price from the GET parameters
        min_price = request.GET.get('min_price')
        max_price = request.GET.get('max_price')
        
        # Filter products based on availability, category, and price range
        products = Product.objects.filter(
            is_available=True,
            category__is_deleted=False,
            category__is_blocked=False,
            productattribute__is_deleted=False,
            productattribute__price__gte=min_price,
            productattribute__price__lte=max_price
        ).distinct().order_by('-id')
        
        # Render the filtered products to HTML
        data = render_to_string('dashboard/product_list.html', {"products": products})
        
        # Return the rendered HTML as a JSON response
        return JsonResponse({"data": data})
    except Exception as e:
        # Handle any exceptions and return an error message
        return JsonResponse({"error": str(e)})

        
        return JsonResponse({"data": data})
    except Exception as e:
        return JsonResponse({"error": str(e)})


def search_and_filter(request):
    search_field = request.GET.get('search_field', '')
    category_id = request.GET.get('category_id')
    subcategory_id = request.GET.get('subcategory_id', None)
    price_filter = request.GET.get('price_filter', None)
    sort_by = request.GET.get('sort_by', None)
    items_per_page = request.GET.get('items_per_page', '9')

    products = Product.objects.all()
    categories = Category.objects.all()

    # Default search for "posters" if no search term is provided
    if not search_field:
        search_field = 'poster'

    # Filter products based on search_field
    if search_field:
        products = products.filter(title__icontains=search_field)

    if category_id and category_id != 'None':
        products = products.filter(category_id=category_id)

    if subcategory_id:
        products = products.filter(sub_category_id=subcategory_id)

    if price_filter:
        if price_filter == 'below_500':
            products = products.filter(product_attributes__price__lt=500)
        elif price_filter == '500_1000':
            products = products.filter(product_attributes__price__gte=500, product_attributes__price__lte=1000)
        elif price_filter == '1000_1500':
            products = products.filter(product_attributes__price__gte=1000, product_attributes__price__lte=1500)
        elif price_filter == '1500_2000':
            products = products.filter(product_attributes__price__gte=1500, product_attributes__price__lte=2000)
        elif price_filter == 'above_2000':
            products = products.filter(product_attributes__price__gt=2000)

    # Annotate products with min and max price
    products = products.annotate(min_price=Min('product_attributes__price'), max_price=Max('product_attributes__price'))

    # Apply sorting by min_price
    if sort_by == 'price_asc':
        products = products.order_by('min_price')
    elif sort_by == 'price_desc':
        products = products.order_by('-min_price')
    elif sort_by == 'title_asc':
        products = products.order_by('title')
    elif sort_by == 'title_desc':
        products = products.order_by('-title')

    # Remove duplicates
    products = products.distinct()

    # Pagination logic
    if items_per_page != 'all':
        paginator = Paginator(products, int(items_per_page))
        page_number = request.GET.get('page')
        products = paginator.get_page(page_number)

    context = {
        'products': products,
        'categories': categories,
        'search_field': search_field,
        'category_id': category_id,
        'subcategory_id': subcategory_id,
        'price_filter': price_filter,
        'sort_by': sort_by,
        'items_per_page': items_per_page,
    }

    return render(request, 'dashboard/search_and_filter.html', context)


#=========================================== views related to shop =================================================================================================================================


def shop(request, category_id=None):
    categories = Category.objects.filter(is_blocked=False)
    selected_category = None
    if category_id:
        selected_category = get_object_or_404(Category, c_id=category_id)
    elif request.method == 'POST':
        category_id = request.POST.get('category_id')
        if category_id:
            selected_category = get_object_or_404(Category, c_id=category_id)

    # Base product query
    products = Product.objects.filter(is_blocked=False)
    if selected_category:
        products = products.filter(category=selected_category)

    # Price filter
    price_filter = request.GET.get('price_filter', None)
    if price_filter:
        if price_filter == 'below_500':
            products = products.filter(product_attributes__price__lt=500)
        elif price_filter == '500_1000':
            products = products.filter(product_attributes__price__gte=500, product_attributes__price__lte=1000)
        elif price_filter == '1000_1500':
            products = products.filter(product_attributes__price__gte=1000, product_attributes__price__lte=1500)
        elif price_filter == '1500_2000':
            products = products.filter(product_attributes__price__gte=1500, product_attributes__price__lte=2000)
        elif price_filter == 'above_2000':
            products = products.filter(product_attributes__price__gt=2000)

    # Annotate products with min and max price for sorting
    products = products.annotate(min_price=Min('product_attributes__price'), max_price=Max('product_attributes__price'))

    # Sorting
    sort_by = request.GET.get('sort_by', None)
    if sort_by == 'price_asc':
        products = products.order_by('min_price')
    elif sort_by == 'price_desc':
        products = products.order_by('-min_price')
    elif sort_by == 'title_asc':
        products = products.order_by('title')
    elif sort_by == 'title_desc':
        products = products.order_by('-title')

    # Remove duplicates
    products = products.distinct()

    # Pagination
    items_per_page = request.GET.get('items_per_page', '10')  # Default to 10 items per page
    if items_per_page != 'all':
        paginator = Paginator(products, int(items_per_page))
        page_number = request.GET.get('page')
        products = paginator.get_page(page_number)

    total_products = products.paginator.count  # Get total product count

    context = {
        'categories': categories,
        'selected_category': selected_category,
        'products': products,
        'total_products': total_products,
        'items_per_page': items_per_page,
        'price_filter': price_filter,
        'sort_by': sort_by,
    }

    return render(request, 'dashboard/shop.html', context)



#=========================================== views related to wishlist =================================================================================================================================


@login_required
def get_wishlist_count(request):
    user = request.user
    wishlist_count = Wishlist.objects.filter(user=user).count() if user.is_authenticated else 0
    return JsonResponse({'wishlist_count': wishlist_count})


@login_required
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


@login_required
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


@login_required
def delete_wishlist(request, pk):
    wishlist = get_object_or_404(Wishlist, id=pk, user=request.user)
    wishlist.delete()
    
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))