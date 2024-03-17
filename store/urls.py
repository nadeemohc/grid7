from django.urls import path
from store import views

app_name = 'store'

urlpatterns = [
    path('', views.home, name='home'),
    path('product_view/<int:product_pid>/', views.product_detailed_view, name='product_view'),
    path('product_detail/<int:p_id>/', views.product_detail, name='product_detail'),
]
