from django.urls import path
from user_cart import views

app_name = 'cart'

urlpatterns = [
    path('view_cart/', views.view_cart, name='view_cart'),
    path('add_to_cart/', views.add_to_cart, name='add_to_cart'),
    path('delete_from_cart/', views.remove_from_cart, name='remove_from_cart'),
    # path('add_to_cart/', views.add_to_cart, name='add_to_cart'),

]