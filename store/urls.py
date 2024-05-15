from django.urls import path
from store import views

app_name = 'store'

urlpatterns = [
    path('', views.home, name='home'),
    path('product_list/', views.list_prod, name='product_list'),
    path('product_list_by_category/<int:category_cid>/',views.product_list_by_category,name = 'product_list_by_category'),
    path('product_view/<int:product_pid>/', views.product_detailed_view, name='product_view'),
    path('get_price/<int:size_id>/', views.get_price, name='get_price'),
    path('user_profile/', views.user_profile, name='user_profile'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('add_address/', views.add_address, name='add_address'),
    path('edit_address/<int:address_id>/', views.edit_address, name='edit_address'),
    path('delete_address/<int:pk>', views.delete_address, name='delete_address'),
    path('change_password/', views.change_password, name='change_password'),
    path('shop/', views.shop, name='shop'),
    path('shop/<int:category_id>/', views.shop, name='shop_by_category'),
    
]
