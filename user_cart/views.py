from django.shortcuts import render, redirect, get_object_or_404
from store.models import *
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
# Create your views here.

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

    return render(request, 'user_cart/cart.html', context)


@login_required
@require_POST
def add_to_cart(request):
    product_id = request.POST.get('product_id')
    quantity = int(request.POST.get('quantity', 1))
    
    product = get_object_or_404(Product, pk=product_id)
    
    # Retrieve the size value from the request.POST dictionary
    size_id = request.POST.get('size')
    
    # If a size is selected, get the corresponding Size object
    if size_id:
        size = get_object_or_404(Size, pk=size_id)
    else:
        size = None

    # Get or create the user's cart
    cart, created = Cart.objects.get_or_create(user=request.user)

    # Add product with selected size and quantity to the user's cart
    cart_item = CartItem.objects.create(user=request.user, cart=cart, product=product, size=size, quantity=quantity)

    return JsonResponse({'success': True})

def remove_from_cart(request):
    pass