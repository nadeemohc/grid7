# from django.shortcuts import render, redirect
# from store.models import CartItem
# from accounts.models import Address
# from django.contrib.auth.decorators import login_required
# from user_cart.views import cart_view
# 
# 
# from django.contrib import messages
# from django.db.models import Sum
# from user_cart.views import cart_view

# @login_required
# def checkout(request):
#     user = request.user

#     # Retrieve the cart view context to get the total cart price
#     cart_view_context = cart_view(request)
#     total_cart_price = cart_view_context.get('total_cart_price', 0)

#     items = CartItem.objects.filter(user=user, is_deleted=False)
#     user_addresses = Address.objects.filter(users=request.user)

#     if request.method == 'POST':
#         # Process the form data
#         street_address = request.POST.get('street_address')
#         city = request.POST.get('city')
#         state = request.POST.get('state')
#         postal_code = request.POST.get('postal_code')
#         country = request.POST.get('country')

#         # Save the address to the database or perform any necessary actions
        
#         # Redirect to a success page or perform any additional actions
#         messages.success(request, 'Address added successfully!')
#         return redirect('checkout')  # Redirect to the checkout page or any other page

#     context = {
#         'items': items,
#         'total_cart_price': total_cart_price,  # Add total_cart_price to the context
#         'user_addresses': user_addresses,
#     }
    
#     # If it's a GET request, render the checkout page with the calculated total
#     return render(request, 'payment/checkout.html', context)


from django.shortcuts import render, redirect
import store
from store.models import CartItem, CartOrder, Payments, ProductOrder, Size
import random
from datetime import datetime
from accounts.models import Address
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from user_cart.views import cart_view  # Importing the cart_view function from the user_cart app

@login_required
def checkout(request):
    user = request.user

    # Retrieve the cart view context to get the total cart price
    cart_view_context = cart_view(request)
    total_cart_price = cart_view_context.get('total_cart_price', 0)

    items = CartItem.objects.filter(user=user, is_deleted=False)
    user_addresses = Address.objects.filter(user=request.user)

    if request.method == 'POST':
        # Process the form data
        street_address = request.POST.get('street_address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        postal_code = request.POST.get('postal_code')
        country = request.POST.get('country')

        # Save the address to the database or perform any necessary actions
        
        # Redirect to a success page or perform any additional actions
        messages.success(request, 'Address added successfully!')
        return redirect('payment:checkout')  # Redirect to the checkout page or any other page

    context = {
        'items': items,
        'total_cart_price': total_cart_price,  # Add total_cart_price to the context
        'user_addresses': user_addresses,
    }
    
    # If it's a GET request, render the checkout page with the calculated total
    return render(request, 'payment/payment.html', context)



@login_required
def payment(request):
    user = request.user
    items = CartItem.objects.filter(user=user, is_deleted=False)
    user_address = Address.objects.filter(user=user).first()
    totals = request.session.get('totals', 0)
    total = request.session.get('total', 0)
    discounts = request.session.get('discounts', 0)

    if request.session.get('order_placed', False):
        del request.session['order_placed']
        return redirect('store:home')

    if request.method == "POST":
        # Retrieve the total cart price from the cart view context
        cart_view_context = cart_view(request)
        total_cart_price = cart_view_context.get('total_cart_price', 0)
        # Handle the Cash on Delivery (COD) payment option
        # This could involve creating an order, updating product stock, etc.
        return pay_cod(request, items, total_cart_price)

    # If it's a GET request or any other method, render the checkout page
    return render(request, 'payment/checkout.html', {
        'user_address': user_address,
        'items': items,
        'total': total,
        'totals': totals,
        'discounts': discounts,
    })


def pay_cod(request, items, total):
    # Handle the Cash on Delivery (COD) payment option
    # This function should contain the logic for COD payment processing
    # You can include order creation, updating product stock, etc.
    user = request.user
    request.session.get('applied_coupon_id', None)
    user_address = Address.objects.filter(user=user).first()

    short_id = str(random.randint(1000, 9999))
    yr = datetime.now().year
    dt = int(datetime.today().strftime('%d'))
    mt = int(datetime.today().strftime('%m'))
    d = datetime(yr, mt, dt).date()
    payment_id = f"PAYMENT-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    current_date = d.strftime("%Y%m%d")
    short_id = str(random.randint(1000, 9999))
    order_numbers = current_date + short_id

    var = CartOrder.objects.create(
        user=user,
        order_number=order_numbers,
        order_total=total,
        selected_address=user_address,
        ip=request.META.get('REMOTE_ADDR')
    )
    var.save()
    payment_instance = Payments.objects.create(
        user=user,
        payment_id=payment_id,
        payment_method='COD',
        amount_paid=total,
        status='Pending',
    )

    var.payment = payment_instance
    var.save()

    cart = CartItem.objects.filter(user=user)

    for item in cart:
        orderedproduct = ProductOrder()
        item.product.stock -= item.quantity
        item.product.save()
        orderedproduct.order = var
        orderedproduct.payment = payment_instance
        orderedproduct.user = user
        orderedproduct.product = item.product
        orderedproduct.quantity = item.quantity
        orderedproduct.product_price = item.product.price
        orderedproduct.size = item.size  # Assuming 'size' is the field name
        orderedproduct.ordered = True
        orderedproduct.save()
        item.delete()
    if 'applied_coupon_id' in request.session:
        request.session.pop('applied_coupon_id')
    # Remove the line below if 'total_cart_price' is used instead of 'total'
    request.session.pop('total_cart_price')

    return redirect('payment:order_success')


@login_required(login_url='user_login')
def order_success(request):
    # Retrieve the latest order for the logged-in user
    order = CartOrder.objects.filter(user=request.user).order_by('-id').first()
    # Retrieve all product orders related to the latest order
    product_orders = ProductOrder.objects.filter(order=order)
    
    # Set a session variable to indicate that an order has been placed
    request.session['order_placed'] = True
    
    # Construct the context to pass to the template
    context = {
        'order': order,
        'order_number': order.order_number if order else None,  # Provide fallback if order is None
        'order_status': order.status if order else None,  # Provide fallback if order is None
        'product_orders': product_orders,
    }
    # Render the template with the context
    return render(request, 'payment/order_detail.html', context)
