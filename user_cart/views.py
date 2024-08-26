from django.shortcuts import render, redirect, get_object_or_404
from store.models import *
from django.urls import reverse
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from decimal import Decimal
from django.db import IntegrityError
import uuid, store, random, sweetify, logging, razorpay
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from . import views
from django.views.decorators.cache import never_cache, cache_control
from django.db.models import Sum
from datetime import datetime
from accounts.models import Address
from accounts.models import Wallet
from django.utils import timezone
from django.template.loader import get_template
from xhtml2pdf import pisa
from io import BytesIO
from user_cart.utils import render_to_pdf
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)

client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

@login_required
def view_cart(request):
    # Check if the order has been processed
    if request.session.get('order_success'):
        # Clear the session flag
        del request.session['order_success']
        # Redirect to empty cart
        return render(request, 'user_cart/cart.html', {'cart_items': [], 'total_cart_price': 0, 'discounts': 0, 'total_after_discount': 0})

    user = request.user
    items = CartItem.objects.filter(user=user, is_deleted=False)
    total_cart_price = Decimal(0)
    cart_items = []

    for cart_item in items:
        product_attribute = cart_item.product
        if product_attribute:
            price = product_attribute.price
            cart_item.subtotal = price * cart_item.quantity
            total_cart_price += cart_item.subtotal
            cart_items.append(cart_item)

    discounts = Decimal(0)
    applied_coupon_id = request.session.get('applied_coupon_id')

    # Handling POST requests
    if request.method == "POST":
        # Applying a coupon
        if 'apply_coupon' in request.POST:
            coupon_code = request.POST.get('coupon_code')
            if coupon_code:
                try:
                    coupon = Coupon.objects.get(
                        code=coupon_code,
                        active=True,
                        active_date__lte=timezone.now(),
                        expiry_date__gte=timezone.now()
                    )
                    # Assuming a percentage discount
                    discounts = (total_cart_price * coupon.discount) / 100
                    request.session['applied_coupon_id'] = coupon.id
                    sweetify.toast(request, f"Coupon {coupon_code} applied successfully!", icon='success', timer=3000)
                except Coupon.DoesNotExist:
                    sweetify.toast(request, "Invalid coupon code or the coupon has expired.", icon='error', timer=3000)
        
        # Removing a coupon
        elif 'remove_coupon' in request.POST:
            if applied_coupon_id:
                del request.session['applied_coupon_id']
                sweetify.toast(request, "Coupon removed successfully.", icon='success', timer=3000)
            return redirect('cart:view_cart')

    # Recalculating the discount if a coupon is applied
    if applied_coupon_id and not discounts:
        try:
            coupon = Coupon.objects.get(id=applied_coupon_id, active=True)
            discounts = (total_cart_price * coupon.discount) / 100
        except Coupon.DoesNotExist:
            del request.session['applied_coupon_id']
            messages.error(request, "The applied coupon is no longer valid.")

    total_after_discount = total_cart_price - discounts

    context = {
        'cart_items': cart_items,
        'total_cart_price': total_cart_price,  # This remains the sum of the original prices
        'discounts': discounts,
        'total_after_discount': total_after_discount,  # This shows the total after applying the discount
        'coupons': Coupon.objects.filter(active=True),  # Show available coupons
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
    # Check if the order has been processed
    if request.session.get('payment_completed'):
        return redirect('cart:view_cart')
    if request.session.get('order_success'):
        # Clear the session flag
        del request.session['order_success']
        # Redirect to empty cart
        return render(request, 'user_cart/cart.html', {'cart_items': [], 'total_cart_price': 0, 'discounts': 0, 'total_after_discount': 0})

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

                # Create ProductOrder entries without reducing stock
                for item in items:
                    product_attribute = item.product
                    ProductOrder.objects.create(
                        order=new_order,
                        user=user,
                        product=product_attribute.product,
                        quantity=item.quantity,
                        product_price=item.product.price,
                        ordered=True,
                        variations=item.product
                    )

                # Clear the coupon from the session
                request.session.pop('applied_coupon_id', None)

                # Redirect to the payment method selection page
                return redirect('cart:payment_method_selection', order_id=new_order.id)
            except Address.DoesNotExist:
                sweetify.toast(request, "Selected address does not exist.", icon='error', timer=3000)
        else:
            sweetify.toast(request, "Please select an address.", icon='error', timer=3000)

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




@login_required
def payment_method_selection(request, order_id):
    try:
        order = CartOrder.objects.get(id=order_id, user=request.user)

        # Check if payment is already completed to avoid duplicate payments
        if request.session.get('payment_completed'):
            return redirect('cart:order_success', order_id=order.id)

    except CartOrder.DoesNotExist:
        sweetify.toast(request, "Order does not exist.", icon='error', timer=5000)
        return redirect('cart:checkout')

    items = CartItem.objects.filter(cart=order.user.cart, is_deleted=False)
    print('inside payment method selection')
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

    try:
        wallet = Wallet.objects.get(user=request.user)
        wallet_balance = wallet.balance
    except Wallet.DoesNotExist:
        wallet_balance = Decimal(0)
        print('wallet_balance fetched:', wallet_balance)

    if request.method == 'POST':
        selected_payment_method = request.POST.get('payment_method')
        print('pyment method=', selected_payment_method)
        if selected_payment_method == 'COD':
            if total_after_discount <= 1000:
                order.status = 'Pending'
                order.payment_method = selected_payment_method
                order.save()
                for item in items:
                    product_attribute = item.product
                    if not product_attribute.reduce_stock(item.quantity):
                        sweetify.toast(request, f"Insufficient stock for {product_attribute.product.title}.", icon='error', timer=5000)
                        return redirect('store:product_view', product_pid=product_attribute.product.id)
                    product_attribute.save()

                order.clear_cart()
                request.session['payment_completed'] = True
                return redirect('cart:order_success', order.id)
            else:
                sweetify.toast(request, "Purchases above 1000 rupees can't be paid Cash on Delivery", icon='error', timer=5000)
        
        elif selected_payment_method == 'Wallet':
            if wallet_balance >= total_after_discount:
                wallet.balance -= total_after_discount
                wallet.save()
                WalletHistory.objects.create(wallet=wallet, transaction_type='Debit', amount=total_after_discount, reason='Purchased Products')
                
                order.status = 'Pending'
                order.payment_method = selected_payment_method
                order.save()

                for item in items:
                    product_attribute = item.product
                    if not product_attribute.reduce_stock(item.quantity):
                        sweetify.toast(request, f"Insufficient stock for {product_attribute.product.title}.", icon='error', timer=5000)
                        return redirect('store:product_view', product_pid=product_attribute.product.id)
                    product_attribute.save()

                order.clear_cart()
                request.session['payment_completed'] = True
                return redirect('cart:order_success', order.id)
            else:
                sweetify.toast(request, '''Insufficient wallet balance, 
                Try razorpay or combine pay.''', icon='error', timer=5000)
        
        elif selected_payment_method == 'Wallet-Razorpay':
            print('inside wallet-razorpay')
            print('wallet_balance before condition:', wallet_balance)
            if wallet_balance > 0:
                print('wallet_balance =', wallet_balance)
                amount_to_pay = total_after_discount - wallet_balance
                print('amount_to_pay', amount_to_pay)
                if amount_to_pay <= 0:
                    amount_to_pay = 0
                wallet.balance = max(wallet_balance - total_after_discount, 0)
                print('wallet balance', wallet.balance)
                wallet.save()
                WalletHistory.objects.create(wallet=wallet, transaction_type='Debit', amount=wallet_balance, reason='Partial Payment')
            else:
                amount_to_pay = total_after_discount
                print('amount to pay in else', amount_to_pay)

            if amount_to_pay > 0:
                razorpay_payment_id = request.POST.get('razorpay_payment_id')
                print('razorpayment_id', razorpay_payment_id)
                if razorpay_payment_id:
                    order.status = 'Completed'
                    order.payment_method = selected_payment_method
                    order.razorpay_payment_id = razorpay_payment_id
                    order.save()
                    print('order.razorpay_payment_id', order.razorpay_payment_id)
                    for item in items:
                        product_attribute = item.product
                        if not product_attribute.reduce_stock(item.quantity):
                            sweetify.toast(request, f"Insufficient stock for {product_attribute.product.title}.", icon='error', timer=5000)
                            return redirect('store:product_view', product_pid=product_attribute.product.id)
                        product_attribute.save()

                    order.clear_cart()
                    request.session['payment_completed'] = True
                    return redirect('cart:order_success', order.id)
                else:
                    sweetify.toast(request, 'Payment failed. Please try again.', icon='error', timer=3000)
                    return redirect('cart:payment_method_selection', order.id)

                client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
                data = {"amount": int(amount_to_pay * 100), "currency": "INR", "payment_capture": 1}
                print('data under client', data)
                try:
                    razorpay_order = client.order.create(data=data)
                    razorpay_order_id = razorpay_order['id']
                except Exception as e:
                    sweetify.toast(request, 'Failed to create Razorpay order.', icon='error', timer=5000)
                    return redirect('cart:checkout')

                context = {
                    'order': order,
                    'items': items,
                    'total_cart_price': total_cart_price,
                    'discounts': discounts,
                    'total_after_discount': total_after_discount,
                    'razorpay_order_id': razorpay_order_id,
                    'razorpay_key_id': settings.RAZORPAY_KEY_ID,
                    'amount_to_pay': amount_to_pay,  # Pass the amount to the template
                    'selected_payment_method': selected_payment_method,  # Pass the selected payment method to the template
                }
                return render(request, 'user_cart/payment_method_selection.html', context)

            else:
                order.status = 'Pending'
                order.payment_method = selected_payment_method
                order.save()
                
                for item in items:
                    product_attribute = item.product
                    if not product_attribute.reduce_stock(item.quantity):
                        sweetify.toast(request, f"Insufficient stock for {product_attribute.product.title}.", icon='error', timer=5000)
                        return redirect('store:product_view', product_pid=product_attribute.product.id)
                    product_attribute.save()

                order.clear_cart()
                request.session['payment_completed'] = True
                return redirect('cart:order_success', order.id)

        elif selected_payment_method == 'Razorpay':
            razorpay_payment_id = request.POST.get('razorpay_payment_id')
            print('razorpayment_id inside razorpay elif', razorpay_payment_id)
            if razorpay_payment_id:
                order.status = 'Completed'
                order.payment_method = selected_payment_method
                order.razorpay_payment_id = razorpay_payment_id
                order.save()

                # Process the items and clear cart
                for item in items:
                    product_attribute = item.product
                    if not product_attribute.reduce_stock(item.quantity):
                        sweetify.toast(request, f"Insufficient stock for {product_attribute.product.title}.", icon='error', timer=5000)
                        return redirect('store:product_view', product_pid=product_attribute.product.id)
                    product_attribute.save()

                order.clear_cart()
                request.session['payment_completed'] = True
                return redirect('cart:order_success', order.id)
            else:
                sweetify.toast(request, 'Payment failed. Please try again.', icon='error', timer=3000)
                return redirect('cart:payment_method_selection', order.id)


    # Razorpay Order Creation for displaying Razorpay payment form initially
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    data = {"amount": int(total_after_discount * 100), "currency": "INR", "payment_capture": 1}
    try:
        razorpay_order = client.order.create(data=data)
        razorpay_order_id = razorpay_order['id']
    except Exception as e:
        sweetify.toast(request, 'Failed to create Razorpay order.', icon='error', timer=5000)
        return redirect('cart:checkout')

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
        
        # Clear the cart items after successful payment
        CartItem.objects.filter(user=request.user, is_deleted=False).update(is_deleted=True)
        
        # Reset session flag
        request.session.pop('payment_completed', None)

        context = {
            'order': order,
            'product_orders': product_orders,
        }
        return render(request, 'user_cart/order_success.html', context)
    except CartOrder.DoesNotExist:
        sweetify.toast(request, 'Order does not exist', icon='error', timer=3000)
        return redirect('store:home')



@login_required
def order_failure(request, order_id):
    try:
        order = CartOrder.objects.get(id=order_id, user=request.user)
        product_orders = ProductOrder.objects.filter(order=order)
    except CartOrder.DoesNotExist:
        sweetify.toast(request, 'Order does not exist', icon='error', timer=3000)


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


def render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None

# def order_invoice(request, order_id):
#     order = get_object_or_404(CartOrder, id=order_id, user=request.user)
#     product_orders = ProductOrder.objects.filter(order=order)
#     context = {
#         'order': order,
#         'product_orders': product_orders,
#     }
#     pdf = render_to_pdf('user_cart/invoice.html', context)
#     if pdf:
#         response = HttpResponse(pdf, content_type='application/pdf')
#         response['Content-Disposition'] = f'attachment; filename="invoice_{order.id}.pdf"'
#         return response
#     return HttpResponse("Error generating PDF")



def order_invoice(request, order_id):
    # Fetch the order and related product orders
    order = get_object_or_404(CartOrder, id=order_id, user=request.user)
    product_orders = ProductOrder.objects.filter(order=order)
    
    # Calculate the total product price and discount amount
    total_product_price = sum(item.product_price for item in product_orders)
    discount_amount = total_product_price - order.order_total
    
    # Prepare the context
    context = {
        'order': order,
        'product_orders': product_orders,
        'discount_amount': discount_amount,
    }
    
    # Render the HTML content
    html_content = render_to_string('user_cart/invoice.html', context)
    
    # Create a BytesIO buffer to hold the PDF
    buffer = BytesIO()
    
    # Convert HTML to PDF
    pdf = pisa.CreatePDF(html_content, dest=buffer)
    
    # Check for errors
    if pdf.err:
        return HttpResponse("Error generating PDF", status=500)
    
    # Get the PDF content from the buffer
    pdf_content = buffer.getvalue()
    buffer.close()
    
    # Return the PDF response
    response = HttpResponse(pdf_content, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{order.id}.pdf"'
    return response
