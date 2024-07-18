from django.shortcuts import render, redirect, get_object_or_404
from store.models import *
from django.urls import reverse
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from decimal import Decimal
from django.db import IntegrityError
import uuid, store, random, sweetify, logging, razorpay
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from . import views
from django.db.models import Sum
from datetime import datetime
from accounts.models import Address
from store.models import CartItem

logger = logging.getLogger(__name__)

client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

@login_required
def view_cart(request):
    user = request.user
    items = CartItem.objects.filter(user=user, is_deleted=False)

    cart_items = []
    total_cart_price = Decimal(0)

    for cart_item in items:
        product_attribute = cart_item.product

        if product_attribute:
            price = product_attribute.price
            size = product_attribute.size
            cart_item.subtotal = price * cart_item.quantity
            total_cart_price += cart_item.subtotal

        cart_items.append(cart_item)

    discounts = 0
    applied_coupon_id = request.session.get('applied_coupon_id')

    if request.method == "POST":
        if 'apply_coupon' in request.POST:
            coupon_code = request.POST.get('coupon_code')
            try:
                coupon = Coupon.objects.get(code=coupon_code, active=True, active_date__lte=timezone.now(),
                                            expiry_date__gte=timezone.now())

                discounts = (total_cart_price * coupon.discount) / 100
                request.session['applied_coupon_id'] = coupon.id

                messages.success(request, 'Coupon applied successfully!')
            except Coupon.DoesNotExist:
                messages.error(request, 'Invalid or expired coupon code')

        elif 'remove_coupon' in request.POST:
            request.session.pop('applied_coupon_id', None)
            discounts = 0
            messages.success(request, 'Coupon removed successfully!')

    if applied_coupon_id:
        try:
            applied_coupon = Coupon.objects.get(id=applied_coupon_id, active=True,
                                                active_date__lte=timezone.now(), expiry_date__gte=timezone.now())
            discounts = (total_cart_price * applied_coupon.discount) / 100
        except Coupon.DoesNotExist:
            request.session.pop('applied_coupon_id', None)

    total_after_discount = total_cart_price - discounts

    coupons = Coupon.objects.filter(active=True, active_date__lte=timezone.now(), expiry_date__gte=timezone.now())

    context = {
        'cart_items': cart_items,
        'total_cart_price': total_cart_price,
        'total_after_discount': total_after_discount,
        'discounts': discounts,
        'coupons': coupons,
    }

    return render(request, 'user_cart/cart.html', context)

@login_required
@require_POST
def add_to_cart(request):
    if request.method == 'POST':
        try:
            product_id = int(request.POST.get('product_id'))
            quantity = int(request.POST.get('quantity', 1))
            size_id = int(request.POST.get('selected_size'))  # Ensure size_id is an integer

            logger.debug(f"Product ID: {product_id}, Quantity: {quantity}, Size ID: {size_id}")

            # Retrieve the product attribute
            product_attribute = get_object_or_404(ProductAttribute, pk=size_id)
            if not product_attribute.check_stock(quantity):
                sweetify.toast(request, "Not enough stock available", timer=3000, icon='warning')
                return redirect('store:product_view', product_pid=product_id)

            if quantity > 5:
                sweetify.toast(request, 'Max limit reached for this product', timer=3000, icon='warning')
                return redirect('store:product_view', product_pid=product_id)

            # Get or create the user's cart
            cart, created = Cart.objects.get_or_create(user=request.user)
            
            # Check if the product is already in the cart
            cart_item, item_created = CartItem.objects.get_or_create(
                user=request.user,
                cart=cart,
                product=product_attribute,
                defaults={'quantity': quantity, 'size': size_id}
            )

            if not item_created:
                # If the total quantity exceeds the max limit, show an error message
                new_quantity = cart_item.quantity + quantity
                # if new_quantity > 5:
                #     sweetify.toast(request, 'Max limit reached for this product', timer=3000, icon='warning')
                #     return redirect('store:product_view', product_pid=product_id)
                cart_item.quantity = new_quantity
                cart_item.save()

            sweetify.toast(request, "Product added to cart successfully", timer=3000, icon='success')
            return redirect('store:product_view', product_pid=product_id)

        except ProductAttribute.DoesNotExist:
            sweetify.toast(request, "Selected size not available", timer=3000, icon='error')
            return redirect('store:product_view', product_pid=product_id)

        except ValueError:
            sweetify.toast(request, "Invalid size or quantity entered", timer=3000, icon='error')
            return redirect('store:product_view', product_pid=product_id)

        except IntegrityError:
            sweetify.toast(request, 'Error adding product to cart', timer=3000, icon='error')
            return redirect('store:product_view', product_pid=product_id)

        except Exception as e:
            logger.error(f'An unexpected error occurred: {e}')
            sweetify.toast(request, 'An unexpected error occurred. Please try again', timer=3000, icon='error')
            return redirect('store:product_list')

    return redirect('store:product_view', product_pid=product_id)


def apply_coupon(request):
    if request.method == "POST":
        coupon_code = request.POST.get("coupon_code")
        try:
            coupon = Coupon.objects.get(code=coupon_code, active=True)
            if coupon.is_active():
                request.session['coupon_id'] = coupon.id
                messages.success(request, "Coupon applied successfully!")
            else:
                messages.error(request, "Coupon is expired or inactive.")
        except Coupon.DoesNotExist:
            messages.error(request, "Invalid coupon code.")
    return redirect('cart:view_cart')




@login_required
def increase_quantity(request, cart_item_id, cart_id):
    try:
        cart_item = get_object_or_404(CartItem, id=cart_item_id, cart_id=cart_id)
        product_attribute = cart_item.product
        if product_attribute.stock > cart_item.quantity:
            if cart_item.quantity < 5:
                cart_item.quantity += 1
                cart_item.save()
                total = cart_item.quantity * product_attribute.price
                total_sum = sum(item.quantity * item.product.price for item in CartItem.objects.filter(cart_id=cart_id))
                return JsonResponse({'q': cart_item.quantity, 'total': total, 'total_sum': total_sum}, status=200)
            else:
                return JsonResponse({'error': 'Max limit reached for this product'}, status=202)
        else:
            return JsonResponse({'error': 'Product is out of stock'}, status=201)
    except CartItem.DoesNotExist:
        return JsonResponse({'error': 'Cart item not found'}, status=404)


@login_required
def decrease_quantity(request, cart_item_id, cart_id):
    try:
        cart_item = get_object_or_404(CartItem, id=cart_item_id, cart_id=cart_id)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
            total = cart_item.quantity * cart_item.product.price
            total_sum = sum(item.quantity * item.product.price for item in CartItem.objects.filter(cart_id=cart_id))
            return JsonResponse({'q': cart_item.quantity, 'total': total, 'total_sum': total_sum}, status=200)
        else:
            return JsonResponse({'error': 'Quantity cannot be less than 1'}, status=400)
    except CartItem.DoesNotExist:
        return JsonResponse({'error': 'Cart item not found'}, status=404)
   


@require_POST
def remove_from_cart(request, cart_item_id):
    
    cart_item = get_object_or_404(CartItem, pk=cart_item_id)
    cart_item.delete()
    sweetify.toast(request, 'Item removed from cart successfully',timer=3000, icon='success')
    return JsonResponse({'message': 'Item removed from cart successfully'}, status=200)


@login_required
def checkout(request):
    user = request.user
    user_cart = Cart.objects.filter(user=user).first()
    total_cart_price = Decimal(0)
    cart_items = []

    if user_cart:
        cart_items = user_cart.items.all()
        for cart_item in cart_items:
            product = cart_item.product
            price = product.price
            cart_item.subtotal = price * cart_item.quantity
            total_cart_price += cart_item.subtotal

    items = CartItem.objects.filter(user=user, is_deleted=False)
    user_addresses = Address.objects.filter(user=user)

    # Fetch applied coupon details
    applied_coupon_id = request.session.get('applied_coupon_id')
    discounts = 0
    if applied_coupon_id:
        try:
            applied_coupon = Coupon.objects.get(id=applied_coupon_id, active=True,
                                                active_date__lte=timezone.now(), expiry_date__gte=timezone.now())
            discounts = (total_cart_price * applied_coupon.discount) / 100
        except Coupon.DoesNotExist:
            request.session.pop('applied_coupon_id', None)

    total_after_discount = total_cart_price - discounts  # Calculate total after applying coupon

    if request.method == 'POST':
        selected_address_id = request.POST.get('existing_address')
        if selected_address_id:
            try:
                selected_address = Address.objects.get(id=selected_address_id, user=user)
                
                # Create the order
                order_number = str(uuid.uuid4())[:12]  # Use first 12 characters of UUID
                new_order = CartOrder.objects.create(
                    user=user,
                    order_number=order_number,
                    order_total=total_after_discount,  # Use total_after_discount here
                    selected_address=selected_address,
                    status='New'
                )

                # Create ProductOrder entries and reduce stock
                for item in items:
                    product_attribute = item.product
                    if product_attribute.reduce_stock(item.quantity):
                        ProductOrder.objects.create(
                            order=new_order,
                            user=user,
                            product=product_attribute.product,
                            quantity=item.quantity,
                            product_price=item.product.price,
                            ordered=True,
                            variations=item.product
                        )
                    else:
                        messages.error(request, f"Insufficient stock for {product_attribute.product.title}.")
                        return redirect('store:product_view', product_pid=product_attribute.product.id)

                # Clear cart after successful order creation
                user_cart.items.all().delete

                # Redirect to the payment method selection page
                return redirect('cart:payment_method_selection', order_id=new_order.id)
            except Address.DoesNotExist:
                messages.error(request, "Selected address does not exist.")
        else:
            messages.error(request, "Please select an address.")

    # Add total price per item to each cart item
    for item in items:
        item.total_price = item.product.price * item.quantity

    context = {
        'items': items,
        'total_cart_price': total_cart_price,  # Pass total_cart_price to template
        'discounts': discounts,
        'total_after_discount': total_after_discount,
        'user_addresses': user_addresses,
    }
    return render(request, 'user_cart/checkout.html', context)


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.conf import settings
import razorpay
# from .models import CartOrder, CartItem
from django.utils import timezone
from decimal import Decimal
from django.contrib.auth.decorators import login_required

@login_required
def payment_method_selection(request, order_id):
    try:
        order = CartOrder.objects.get(id=order_id, user=request.user)
    except CartOrder.DoesNotExist:
        messages.error(request, "Order does not exist.")
        return redirect('cart:checkout')

    items = CartItem.objects.filter(cart=order.user.cart, is_deleted=False)
    
    total_cart_price = Decimal(0)
    for item in items:
        item.total_price = item.product.price * item.quantity
        total_cart_price += item.total_price

    applied_coupon_id = request.session.get('applied_coupon_id')
    discounts = Decimal(0)
    if applied_coupon_id:
        try:
            applied_coupon = Coupon.objects.get(id=applied_coupon_id, active=True,
                                                active_date__lte=timezone.now(), expiry_date__gte=timezone.now())
            discounts = (total_cart_price * applied_coupon.discount) / 100
        except Coupon.DoesNotExist:
            request.session.pop('applied_coupon_id', None)

    total_after_discount = total_cart_price - discounts

    if request.method == 'POST':
        selected_payment_method = request.POST.get('payment_method')
        print(f'Selected payment method: {selected_payment_method}')  # Debug print statement
        
        if selected_payment_method == 'COD':
            print('Inside COD selection')
            order.status = 'Pending'
            order.payment_method = selected_payment_method
            order.save()
            order.clear_cart()
            return redirect('cart:order_success', order.id)
        
        elif selected_payment_method == 'Wallet':
            print('Inside Wallet selection')
            if request.user.wallet_balance >= total_after_discount:
                request.user.wallet_balance -= total_after_discount
                request.user.save()
                order.status = 'Pending'
                order.payment_method = selected_payment_method
                order.save()
                order.clear_cart()
                return redirect('cart:order_success', order.id)
            else:
                messages.error(request, 'Insufficient wallet balance.')
        
        elif selected_payment_method == 'Razorpay':
            print('Inside Razorpay selection')
            razorpay_payment_id = request.POST.get('razorpay_payment_id')
            print(f'payment id: {razorpay_payment_id}')
            if not razorpay_payment_id:
                messages.error(request, 'Payment failed. Please try again.')
                return redirect('cart:payment_method_selection', order.id)
            order.status = 'Completed'
            order.payment_method = selected_payment_method
            order.razorpay_payment_id = razorpay_payment_id
            order.save()
            order.clear_cart()
            return redirect('cart:order_success', order.id)
        
        else:
            messages.error(request, 'Invalid payment method selected.')
            return redirect('cart:payment_method_selection', order.id)

    # Razorpay Order Creation
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    data = {
        "amount": int(total_after_discount * 100),  # amount in paise
        "currency": "INR",
        "payment_capture": 1,
    }
    razorpay_order = client.order.create(data=data)
    razorpay_order_id = razorpay_order['id']

    context = {
        'order': order,
        'items': items,
        'total_cart_price': total_cart_price,
        'discounts': discounts,
        'total_after_discount': total_after_discount,
        'razorpay_order_id': razorpay_order_id,
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
    }

    return render(request, 'user_cart/payment_method_selection.html', context)




@login_required
def order_success(request, order_id):
    try:
        order = CartOrder.objects.get(id=order_id, user=request.user)
        product_orders = ProductOrder.objects.filter(order=order)
    except CartOrder.DoesNotExist:
        messages.error(request, "Order does not exist.")
        return redirect('store:home')

    context = {
        'order': order,
        'product_orders': product_orders,
    }
    return render(request, 'user_cart/order_success.html', context)


@login_required
def payment(request, order_id):
    user = request.user
    order = get_object_or_404(CartOrder, id=order_id, user=user)

    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')

        if payment_method:
            # Assume payment is successful and update the order status
            Payments.objects.create(
                user=user,
                payment_id=str(uuid.uuid4()),  # Example payment ID
                payment_method=payment_method,
                amount_paid=order.order_total,
                status='Completed'
            )
            order.status = 'Paid'
            order.save()

            messages.success(request, "Your payment was successful!")
            return redirect('cart:order_confirmation', order_id=order.id)
        else:
            messages.error(request, "Please select a payment method.")

    context = {
        'order': order,
    }
    return render(request, 'user_cart/payment.html', context)


@login_required
def order_confirmation(request, order_id):
    user = request.user
    order = get_object_or_404(CartOrder, id=order_id, user=user)
    context = {
        'order': order,
    }
    return render(request, 'user_cart/order_confirmation.html', context)


# def place_order(request):
#     user = request.user 
#     items = CartItem.objects.filter(user=user, is_deleted=False)
#     request.session.get('applied_coupon_id', None)  
#     request.session.get('totals', 0)
#     total = request.session.get('total', 0)
#     request.session.get('discounts', 0)
   

#     # user_addresses = items.first().address

#     short_id = str(random.randint(1000, 9999))
#     yr = datetime.now().year
#     dt = int(datetime.today().strftime('%d'))
#     mt = int(datetime.today().strftime('%m'))
#     d = datetime(yr, mt, dt).date()
#     payment_id = f"PAYMENT-{timezone.now().strftime('%Y%m%d%H%M%S')}"

#     current_date = d.strftime("%Y%m%d")
#     short_id = str(random.randint(1000, 9999))
#     order_numbers = current_date + short_id 
#     coupons = []

#     for item in items:
#         coupon = item.coupon
#         coupons.append(coupon)

#     if coupons:
#         coupon = coupons[0]
#     else:
#         coupon = None

#     var=CartOrder.objects.create(
#         user=request.user,
#         order_number=order_numbers,
#         order_total= total,
#         coupen=coupon,
#         selected_address=user_addresses,
#         ip=request.META.get('REMOTE_ADDR')    
#     )
#     var.save()
#     payment_instance=Payments.objects.create(
#         user=request.user,
#         payment_id=payment_id,
#         payment_method='COD',
#         amount_paid= total,
#         status='Pending',
                
#     )
        
#     var.payment=payment_instance
#     var.save()
            
#     cart=CartItem.objects.filter(user=request.user)
            
#     for item in cart:
#         orderedproduct=ProductOrder()
#         item.product.stock-=item.quantity
#         item.product.save()
#         orderedproduct.order=var
#         orderedproduct.payment=payment_instance
#         orderedproduct.user=request.user
#         orderedproduct.product=item.product.product
#         orderedproduct.quantity=item.quantity
#         orderedproduct.product_price=item.product.price
#         product_attribute = ProductAttribute.objects.get(product=item.product.product, color=item.product.color)
#         orderedproduct.variations = product_attribute
#         orderedproduct.ordered=True
#         orderedproduct.save()
#         item.delete()  
#     if 'applied_coupon_id' in request.session:
#         request.session.pop('applied_coupon_id')     
#     request.session.pop('totals')
#     total = request.session.pop('total')
#     request.session.pop('discounts')
        
#     return redirect('cart:success')

# def success(request):
    
#     return render(request, 'user_cart/success_page.html')