from django.urls import path
from user_cart import views

app_name = 'cart'

urlpatterns = [
    # Cart functionalities
    path('cart_view/', views.view_cart, name='view_cart'),
    path('add_to_cart/', views.add_to_cart, name='add_to_cart'),
    path('increase_quantity/<int:cart_item_id>/<int:cart_id>/', views.increase_quantity, name='increase_quantity'),
    path('decrease_quantity/<int:cart_item_id>/<int:cart_id>/', views.decrease_quantity, name='decrease_quantity'),
    path('remove_from_cart/<int:cart_item_id>/', views.remove_from_cart, name='remove_from_cart'),

    #  Coupon Functionalities
    path('apply_coupon/', views.apply_coupon, name='apply_coupon'),

    #  Checkout and Payment
    path('select_payment_method/<int:order_id>/', views.payment_method_selection, name='payment_method_selection'),
    path('checkout/', views.checkout, name='checkout'),  

    #  Order success and failure
    path('order_success/<int:order_id>/', views.order_success, name='order_success'),
    path('order_failure/<int:order_id>/', views.order_failure, name='order_failure'),
    
    #  Invoice downloading
    path('order/<int:order_id>/invoice/', views.order_invoice, name='order_invoice'),
    
]
