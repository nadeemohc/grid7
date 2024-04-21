from django.shortcuts import render, get_object_or_404
from user_cart.cart import Cart
from store.models import Product
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
# Create your views here.

def view_cart(request):
    # Get the cart
    cart = Cart(request)
    cart_products = cart.get_prods()
    quantities = cart.get__quants()
    context = {
        'quantities': quantities,
        'cart_products': cart_products,
        'title': 'Cart',
    }
    return render(request, 'user_cart/cart.html', context)

# @login_required
def add_to_cart(request):
    # Get the cart
    cart = Cart(request)
    # test for POST
    if request.POST.get('action') == 'post':
        # Get stuff
        product_id = int(request.POST.get('product_id'))
        product_qty = int(request.POST.get('product_qty'))

        # lookup product in DB
        product = get_object_or_404(Product, p_id=product_id)
        
        # Save to session
        cart.add(product=product, quantity=product_qty)

        # Get cart quantity 
        cart_quantity = cart.__len__()

        # return response
        # response = JsonResponse({'Product Name': product.title})
        response = JsonResponse({'qty': cart_quantity})
        return response

    # return render(request, 'dashboard/user_cart/cart.html')

