from django.urls import path
from user_cart import views

app_name = 'cart'

urlpatterns = [
    # path('add_to_cart/', views.add_to_cart, name='add_to_cart'),
    # path('delete_from_cart/', views.remove_from_cart, name='remove_from_cart'),
    path('view_cart/', views.cart_view, name='view_cart'),
    path('add_to_cart/', views.add_to_cart, name='add_to_cart'),
    path('remove_from_cart/<int:cart_item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('decrease_quantity/<int:cart_item_id>/<int:cart_id>/', views.decrease_quantity, name='decrease_quantity'),
    path('increase_quantity/<int:cart_item_id>/<int:cart_id>/', views.increase_quantity, name='increase_quantity'),
]