from django.urls import path
from user_cart import views

app_name = 'cart'

urlpatterns = [
    path('cart_view/', views.view_cart, name='view_cart'),
    path('apply_coupon/', views.apply_coupon, name='apply_coupon'),
    path('add_to_cart/', views.add_to_cart, name='add_to_cart'),
    path('increase_quantity/<int:cart_item_id>/<int:cart_id>/', views.increase_quantity, name='increase_quantity'),
    path('decrease_quantity/<int:cart_item_id>/<int:cart_id>/', views.decrease_quantity, name='decrease_quantity'),
    path('remove_from_cart/<int:cart_item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),  
    path('order_success/<int:order_id>/', views.order_success, name='order_success'),
    path('select_payment_method/<int:order_id>/', views.payment_method_selection, name='payment_method_selection'),
    path('order_confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    # path('razorpay_payment/<int:order_id>/<str:razorpay_order_id>/', views.razorpay_payment, name='razorpay_payment'),
    # path('razorpay-payment/<int:order_id>/', views.razorpay_payment, name='razorpay_payment'),
]
