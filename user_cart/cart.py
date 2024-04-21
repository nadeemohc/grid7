from store.models import Product


class Cart():
    
    def __init__(self, request):
        self.session = request.session

        # Get the current session key if it exists
        cart = self.session.get('session_key')

        # If the user is new no sesion key. So create one
        if 'session_key' not in request.session:
            cart = self.session['session_key'] = {}

        # Make sure the cart is available on all pages
        self.cart = cart

    def add(self, product, quantity):
        product_id = str(product.p_id)
        product_qty = str(quantity)

        # logic
        if product_id in self.cart:
            pass
        else:
            # self.cart[product_id] = {'price': str(product.price)}
            self.cart[product_id] = int(product_qty)

        self.session.modified = True
        
    def __len__(self):
        return len(self.cart)

    def get_prods(self):
        # Get ids from cart
        product_ids = self.cart.keys()
        # Use ids to lookup products in database model
        products = Product.objects.filter(p_id__in = product_ids)
        # Return the looked up products
        return products

    def get__quants(self):
        quantities = self.cart
        return quantities