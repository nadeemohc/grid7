from django.shortcuts import render, redirect, get_object_or_404
from store.models import *
from django.urls import reverse
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from decimal import Decimal
import store, random
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
    print(cart_item)
    
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
def checkout(request):
    user = request.user

    # Retrieve the user's cart if it exists
    user_cart = Cart.objects.filter(user=user).first()

    cart_items = []
    total_cart_price = Decimal(0)  # Initialize total_cart_price as Decimal

    if user_cart:
        cart_items = user_cart.items.all()

        for cart_item in cart_items:
            # Access the associated product
            product = cart_item.product
            
            # Access the price from one of the product attributes
            # Assuming there's at least one product attribute associated with the product
            # You may need to adjust this logic based on your data model
            # product_attribute = product.productattribute_set.first()
            product_attribute = product  # Assuming the ProductAttribute itself represents the product variant

            if product_attribute:
                price = product_attribute.price
                
                # Calculate the subtotal for each item (product price * quantity)
                cart_item.subtotal = price * cart_item.quantity

                # Add the subtotal to the total_cart_price
                total_cart_price += cart_item.subtotal

    items = CartItem.objects.filter(user=user, is_deleted=False)
    user_addresses = Address.objects.filter(user=user)
    print(len(user_addresses))
    if request.method == 'POST':
        street_address = request.POST.get('street_address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        postal_code = request.POST.get('postal_code')
        country = request.POST.get('country')
        
        # Save the address to the database or perform any necessary actions
        address = Address.objects.create(
            user = request.user,
            street_address = street_address,
            city = city,
            state = state,
            postal_code = postal_code,
            country = country,
        )
        print(add)
        # Redirect to a success page or perform any additional actions
        messages.success(request, 'Address added successfully!')
        return redirect('cart:checkout')  # Redirect to the checkout page or any other page

    context = {
        'items': items,
        'total_cart_price': total_cart_price,  # Add total_cart_price to the context
        'user_addresses': user_addresses,
    }
    return render(request, 'user_cart/checkout.html', context)

def payment(request):
    return render(request, 'user_cart/payment.html')