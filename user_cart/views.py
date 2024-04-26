from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product, Size, CartItem, Cart
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
# Create your views here.

# def view_cart(request):
#     # Retrieve the user's cart
#     cart, created = Cart.objects.get_or_create(user=request.user)
    
#     # Retrieve cart items associated with the user's cart
#     cart_items = CartItem.objects.filter(cart=cart)

#     # Initialize subtotal
#     sub_total = 0

#     # Calculate subtotal for all cart items
#     for cart_item in cart_items:
#         # Calculate subtotal for each cart item
#         item_subtotal = cart_item.product.price * cart_item.quantity
        
#         # Add item subtotal to total
#         sub_total += item_subtotal

#         # Pass size information to template
#         # cart_item.size_info = ", ".join(size.size for size in cart_item.size.all())
#         cart_item.size_info = cart_item.size.size  # Assuming 'size' is the field name


#     context = {
#         'cart_items': cart_items,
#         'sub_total': sub_total,
#     }

#     return render(request, 'user_cart/cart.html', context)


def view_cart(request):
    # Retrieve the user's cart if it exists
    user_cart = Cart.objects.filter(user=request.user).first()

    if user_cart:
        cart_items = user_cart.items.all()

        for cart_item in cart_items:
            cart_item.total_price = cart_item.product.price * cart_item.quantity
        total_cart_price = sum(cart_item.total_price for cart_item in cart_items)
    else:
        cart_items = []
        total_cart_price = 0
    
        cart_item.size_info = cart_item.size.size  # Assuming 'size' is the field name

    context = {
          'cart_items': cart_items, 
          'total_cart_price': total_cart_price 
       }


# def view_cart(request):
#     # Retrieve the user's cart
#     cart, created = Cart.objects.get_or_create(user=request.user)
    
#     # Retrieve cart items associated with the user's cart
#     cart_items = CartItem.objects.filter(cart=cart)

#     # Initialize subtotal
#     sub_total = 0
#     for cart_item in cart_items:
#         product_sub = cart_item.product.price * cart_item.quantity
#         prod_sub = sum(product_sub for cart_item in cart_items)
#     # Calculate subtotal for all cart items
#     for cart_item in cart_items:
#         # Calculate subtotal for each cart item
#         item_subtotal = cart_item.product.price * cart_item.quantity
        
#         # Add item subtotal to total
#         sub_total += item_subtotal

#         # Pass size information to template
#         cart_item.size_info = cart_item.size.size  # Assuming 'size' is the field name

#     context = {
#         'cart_items': cart_items,
#         'prod_sub': prod_sub,
#         'sub_total': sub_total,
#     }

    return render(request, 'user_cart/cart.html', context)



    # Retrieve the user's cart if it exists
    # user_cart = Cart.objects.filter(user=request.user).first()

    # if user_cart:
    #     cart_items = user_cart.items.all()

    #     for cart_item in cart_items:
    #         cart_item.total_price = cart_item.product.price * cart_item.quantity
    #     total_cart_price = sum(cart_item.total_price for cart_item in cart_items)
    # else:
    #     cart_items = []
    #     total_cart_price = 0

    # context = {
    #       'cart_items': cart_items, 
    #       'total_cart_price': total_cart_price 
    #    }
    

    # return render(request, "core/cart_view.html",context)

# @login_required
# def add_to_cart(request):
#     if request.method == 'POST':
#         product_id = request.POST.get('product_id')
#         size_id = request.POST.get('size')
#         quantity = int(request.POST.get('quantity', 1))
        
#         # Get the product and size objects
#         product = get_object_or_404(Product, p_id=product_id)
#         size = get_object_or_404(Size, id=size_id)

#         # Get or create the user's cart
#         cart, created = Cart.objects.get_or_create(user=request.user)

#         # Add product with selected size and quantity to the user's cart
#         cart_item = CartItem.objects.create(user=request.user, cart=cart, product=product, quantity=quantity)
#         cart_item.size = size


#         return redirect('cart:view_cart')  # Redirect to cart view after adding to cart
#     else:
#         # Handle GET request if needed
#         pass


@login_required
def add_to_cart(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        size_id = request.POST.get('size')
        quantity = int(request.POST.get('quantity', 1))
        
        # Get the product and size objects
        product = get_object_or_404(Product, p_id=product_id)
        size = get_object_or_404(Size, id=size_id)

        # Get or create the user's cart
        cart, created = Cart.objects.get_or_create(user=request.user)

        # Add product with selected size and quantity to the user's cart
        cart_item = CartItem.objects.create(user=request.user, cart=cart, product=product, size=size, quantity=quantity)

        return redirect('cart:view_cart')  # Redirect to cart view after adding to cart
    else:
        # Handle GET request if needed
        pass


def remove_from_cart(request):
    pass