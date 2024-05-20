from django.shortcuts import render, redirect, get_object_or_404
from store.models import *
from django.urls import reverse
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from decimal import Decimal
import store, random
import uuid 
from . import views
from datetime import datetime
from accounts.models import Address
from store.models import CartItem



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





import logging

logger = logging.getLogger(__name__)
@login_required
@require_POST
def add_to_cart(request):
    product_id = int(request.POST.get('product_id'))
    quantity = int(request.POST.get('quantity', 1))
    size_id = request.POST.get('selected_size')  # Correctly retrieving the selected size ID
    print(product_id, quantity, size_id)
    logger.debug(f"Product ID: {product_id}, Quantity: {quantity}, Size ID: {size_id}")

    product = ProductAttribute.objects.get(pk=size_id)
    print(product)
    # Get or create the user's cart
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    # Add the product to the cart with the selected size
    cart_item = CartItem.objects.create(user=request.user, cart=cart, product=product, quantity=quantity, size=size_id)
  
    # Optionally, you can display a success message
    messages.success(request, f"{product} added to cart.")
    
    # Redirect to the product view page with the product_pid parameter
    return redirect(reverse('store:product_view', kwargs={'product_pid': product_id}))


# @login_required
# @require_POST
# def increase_quantity(request, cart_item_id):
#     cart_item = get_object_or_404(CartItem, pk=cart_item_id)
#     if cart_item.product.stock >= cart_item.quantity + 1:
#         cart_item.quantity += 1
#         cart_item.save()
#         # Calculate total and subtotal
#         total_price = cart_item.product.price * cart_item.quantity
#         return JsonResponse({'quantity': cart_item.quantity, 'total': total_price})
#     else:
#         # Return status 201 if product is out of stock
#         return JsonResponse({'error': 'Product is out of stock'}, status=201)

# @login_required
# @require_POST
# def decrease_quantity(request, cart_item_id):
#     cart_item = get_object_or_404(CartItem, pk=cart_item_id)
#     if cart_item.quantity > 1:
#         cart_item.quantity -= 1
#         cart_item.save()
#         # Calculate total and subtotal
#         total_price = cart_item.product.price * cart_item.quantity
#         return JsonResponse({'quantity': cart_item.quantity, 'total': total_price})
#     else:
#         # Return status 400 if quantity is already 1
#         return JsonResponse({'error': 'Quantity cannot be less than 1'}, status=400)






    



def decrease_quantity(request, cart_item_id,cart_id):
    print("decrese in")
    cart_item = get_object_or_404(CartItem, pk=cart_item_id)
    # print(cart_item)
    
    if cart_item.quantity > 1:
        cart_item.quantity = cart_item.quantity-1
        cart_item.save()
        
        print(cart_item.quantity)
        total_price = cart_item.product.price * cart_item.quantity
        cart_item.save()
        print(total_price)

        all_products = CartItem.objects.filter(cart_id=cart_id)

        total_quantity = 0
        total = 0

        for cart_item in all_products:
            total_quantity += cart_item.quantity
            total += cart_item.product.price * cart_item.quantity
            print(total)

        return JsonResponse({'q': cart_item.quantity,'total':total_price,'total_sum':total}, status=200)
    else:
        return JsonResponse({'error': 'Quantity cannot be less than 1'}, status=400)
    
    
def increase_quantity(request, cart_item_id,cart_id):
    print('inside inseidhfkasdhfkhk')
    cart_item = get_object_or_404(CartItem, pk=cart_item_id)

    # print(cart_item)

    # if cart_item.quantity < cart_item.product.stock:
    cart_item.quantity += 1
    cart_item.save()
    
    

    total_price = cart_item.product.price * cart_item.quantity
    cart_item.save()

    all_products = CartItem.objects.filter(cart_id=cart_id)
       
    total = 0
        
        
    for cart_i in all_products:
        
        total += cart_i.product.price * cart_i.quantity
        
        
    return JsonResponse({'q': cart_item.quantity , 'total':total_price,'total_sum':total}, status=200)
    # else:
    return JsonResponse({'msg':'This product is out of stock.'},status = 201),
   


@require_POST
def remove_from_cart(request, cart_item_id):
    
    cart_item = get_object_or_404(CartItem, pk=cart_item_id)
    cart_item.delete()
    return JsonResponse({'message': 'Item removed from cart successfully'}, status=200)


    from django.shortcuts import render, redirect


@login_required
@login_required

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

                # Create ProductOrder entries
                for item in items:
                    ProductOrder.objects.create(
                        order=new_order,
                        user=user,
                        product=item.product.product,
                        quantity=item.quantity,
                        product_price=item.product.price,
                        ordered=True,
                        variations=item.product
                    )

                # Delete all items from the user's cart after creating the order
                user_cart.items.all().delete()

                return render(request, 'user_cart/order_success.html', {
                    'order': new_order,
                    'product_orders': ProductOrder.objects.filter(order=new_order),
                })
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