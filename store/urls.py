from django.urls import path
from store import views

app_name = 'store'

urlpatterns = [
    path('', views.home, name='home'),
    path('product_view/<int:product_pid>/', views.product_detailed_view, name='product_view'),
    path('product_detail/<int:product_id>/', views.product_detail, name='product_detail'),
    path('user_profile/', views.user_profile, name='user_profile'),
]
