from django.shortcuts import render, get_object_or_404
from store.models import Cart, CartItem
from store.models import Product
from django.contrib import messages
from django.db.models import Sum
from django.utils import timezone
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
# Create your views here.

@login_required
def cart_view(request):
    # Retrieve the user's cart if it exists
    user_cart = Cart.objects.filter(user=request.user).first()

    if user_cart:
        cart_items = user_cart.items.all()

        # Calculate total cart price
        total_cart_price = sum(cart_item.product.price * cart_item.quantity for cart_item in cart_items)
    else:
        cart_items = []
        total_cart_price = Decimal('0.00')  # Initialize as Decimal

    # Convert total_cart_price to float for session storage
    total_cart_price = float(total_cart_price)

    # Store total_cart_price in the session
    request.session['total_cart_price'] = total_cart_price

    context = {
        'cart_items': cart_items,
        'total_cart_price': total_cart_price
    }

    return render(request, "user_cart/cart.html", context)

@login_required
def add_to_cart(request):
    if request.method == 'GET':
        product_pid = request.GET.get('product_pid')
        if product_pid:
            try:
                product = get_object_or_404(Product, p_id=product_pid)
                user_cart, created = Cart.objects.get_or_create(user=request.user)
                cart_item, item_created = CartItem.objects.get_or_create(cart=user_cart, product=product, user=request.user)

                if item_created:
                    message = f"{product.title} added to cart"
                else:
                    message = f"{product.title} is already in your cart"

                return JsonResponse({'message': message})
            except Product.DoesNotExist:
                pass

    return HttpResponseBadRequest("Invalid request")


def decrease_quantity(request, cart_item_id,cart_id):
    cart_item = get_object_or_404(CartItem, pk=cart_item_id)
    
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
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

        return JsonResponse({'quantity': cart_item.quantity,'total':total_price,'total_sum':total}, status=200)
    else:
        return JsonResponse({'error': 'Quantity cannot be less than 1'}, status=400)
    
    
def increase_quantity(request, cart_item_id,cart_id):
    cart_item = get_object_or_404(CartItem, pk=cart_item_id)
    print(cart_item)

    if cart_item.quantity < cart_item.product.stock:
        cart_item.quantity += 1
        cart_item.save()
        
    

        total_price = cart_item.product.price * cart_item.quantity
        cart_item.save()

        all_products = CartItem.objects.filter(cart_id=cart_id)
       
        total = 0
        
        
        for cart_i in all_products:
            
            total += cart_i.product.price * cart_i.quantity
            
        
        return JsonResponse({'q': cart_item.quantity , 'total':total_price,'total_sum':total}, status=200)
    else:
        return JsonResponse({'msg':'This product is out of stock.'},status = 201),

@require_POST
def remove_from_cart(request, cart_item_id):
    
    cart_item = get_object_or_404(CartItem, pk=cart_item_id)
    cart_item.delete()
    return JsonResponse({'message': 'Item removed from cart successfully'}, status=200)