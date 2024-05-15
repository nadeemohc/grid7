from django.urls import path
from user_cart import views

app_name = 'cart'

urlpatterns = [
    path('view_cart/', views.view_cart, name='view_cart'),
    path('add_to_cart/', views.add_to_cart, name='add_to_cart'),
    path('increase_quantity/<int:cart_item_id>/<int:cart_id>/', views.increase_quantity, name='increase_quantity'),
    path('decrease_quantity/<int:cart_item_id>/<int:cart_id>/', views.decrease_quantity, name='decrease_quantity'),
    path('remove_from_cart/<int:cart_item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('payment/', views.payment, name='payment'),

]