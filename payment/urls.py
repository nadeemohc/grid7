from django.urls import path
from payment import views

app_name = 'payment'

urlpatterns = [
    path('checkout/', views.payment, name='checkout'),
    path('payment/', views.payment, name='payment'),
    path('order_success/', views.order_success, name='order_success'),
]