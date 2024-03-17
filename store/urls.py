from django.urls import path
from store import views

app_name = 'store'

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.user_prod_list, name='products'),
    path('product_view/', views.product_detailed_view, name='product_view'),
    path('product_detail/<int:pk>/', views.product_detail, name='product_detail'),
]
