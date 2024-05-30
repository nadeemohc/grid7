# store/context_processors.py

from store.models import Cart

def cart_item_count(request):
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            item_count = cart.items.count()
        except Cart.DoesNotExist:
            item_count = 0
    else:
        item_count = 0

    return {'item_count': item_count}
