from .cart import Cart

# Create context processors so the cart can work on all pages on our site
def cart(request):
    return {'cart': Cart(request)}