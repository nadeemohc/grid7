# store/context_processors.py

from store.models import Cart, Wishlist

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

    
def wishlist_item_count(request):
    if request.user.is_authenticated:
        wishlist_count = Wishlist.objects.filter(user=request.user).count()
    else:
        wishlist_count = 0
    return {'wishlist_count': wishlist_count}