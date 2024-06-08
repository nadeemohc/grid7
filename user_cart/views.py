from django.shortcuts import render, redirect, get_object_or_404
from store.models import *
from django.urls import reverse
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from decimal import Decimal
from django.db import IntegrityError
import uuid, store, random, sweetify, logging
from django.conf import settings
from . import views
from datetime import datetime
from accounts.models import Address
from store.models import CartItem

logger = logging.getLogger(__name__)

def view_cart(request):
    # Retrieve the user's cart if it exists
    user = request.user
    items = CartItem.objects.filter(user=user, is_deleted=False)

    cart_items = []
    total_cart_price = Decimal(0)  # Initialize total_cart_price as Decimal

    for cart_item in items:
        # Access the associated product
        product = cart_item.product
        
        # Access the price from one of the product attributes
        # Assuming there's at least one product attribute associated with the product
        # You may need to adjust this logic based on your data model
        # product_attribute = product.productattribute_set.first()
        product_attribute = cart_item.product  # Assuming the ProductAttribute itself represents the product variant

        if product_attribute:
            price = product_attribute.price
            size = product_attribute.size
            
            # Calculate the subtotal for each item (product price * quantity)
            cart_item.subtotal = price * cart_item.quantity

            # Add the subtotal to the total_cart_price
            total_cart_price += cart_item.subtotal

        cart_items.append(cart_item)

    context = {
        'cart_items': cart_items,
        'total_cart_price': total_cart_price,
    }

    # Pass the subtotal and total_cart_price to the frontend
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

    if user_cart:
        cart_items = user_cart.items.all()
        for cart_item in cart_items:
            product = cart_item.product
            price = product.price
            cart_item.subtotal = price * cart_item.quantity
            total_cart_price += cart_item.subtotal

    items = CartItem.objects.filter(user=user, is_deleted=False)
    user_addresses = Address.objects.filter(user=user)

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
                    order_total=total_cart_price,
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

                # Redirect to the payment method selection page
                return redirect('cart:payment_method_selection', order_id=new_order.id)
            except Address.DoesNotExist:
                messages.error(request, "Selected address does not exist.")
        else:
            messages.error(request, "Please select an address.")

    context = {
        'items': items,
        'total_cart_price': total_cart_price,
        'user_addresses': user_addresses,
    }
    return render(request, 'user_cart/checkout.html', context)


@login_required
def payment_method_selection(request, order_id):
    try:
        order = CartOrder.objects.get(id=order_id, user=request.user)
    except CartOrder.DoesNotExist:
        messages.error(request, "Order does not exist.")
        return redirect('cart:checkout')

    items = CartItem.objects.filter(cart=order.user.cart, is_deleted=False)

    if request.method == 'POST':
        selected_payment_method = request.POST.get('payment_method')
        if selected_payment_method == 'COD':
            order.status = 'Pending'
            order.save()
            order.clear_cart()  # Clear the cart items
            return redirect('cart:order_success', order_id=order.id)
        elif selected_payment_method == 'Razorpay':
            return redirect('cart:razorpay_payment', order_id=order.id)
        else:
            messages.error(request, "Invalid payment method selected.")
            return redirect('cart:payment_method_selection', order_id=order.id)

    context = {
        'order': order,
        'items': items, 
        'total_cart_price': order.order_total,
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





