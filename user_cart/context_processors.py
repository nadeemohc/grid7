from store.models import CartItem

def cart_item_count(request):
    if request.user.is_authenticated:
        item_count = CartItem.objects.filter(cart__user=request.user).count()
    else:
        item_count = 0
    return {'item_count': item_count}
