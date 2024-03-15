from django.urls import path
from cust_admin import views

app_name = 'cust_admin'

urlpatterns = [
    path('admin_dashboard/', views.dashboard, name='admin_dashboard'),
    path('user_view/<str:username>/', views.user_view, name='user_view'),
    path('user_list/', views.user_list, name='user_list'),
    path('user_block/<str:username>/', views.user_block_unblock, name='user_block'),
    path('add_product/', views.add_product, name='add_product'),
    path('prod_list/', views.prod_list, name='prod_list'),
    path('category_list', views.category_list, name='category_list'),
    path('add_category/', views.add_category, name='add_category'),
    path('category_unlist/<int:c_id>/', views.category_list_unlist, name='category_unlist'),
    path('add_sub/', views.add_sub, name='add_sub'),
    path('list_products/', views.prod_list, name='list_prod'),
]