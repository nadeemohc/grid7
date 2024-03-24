from django.urls import path
from store import views

app_name = 'store'

urlpatterns = [
    path('', views.home, name='home'),
    path('product_view/<int:product_pid>/', views.product_detailed_view, name='product_view'),
    path('product_detail/<int:product_id>/', views.product_detail, name='product_detail'),
    path('user_profile/', views.user_profile, name='user_profile'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('add_address/', views.add_address, name='add_address'),
    path('edit_address/<int:address_id>/', views.edit_address, name='edit_address'),
    path('delete_address/<int:pk>', views.delete_address, name='delete_address'),
    path('change_password/', views.change_password, name='change_password'),
    
]
