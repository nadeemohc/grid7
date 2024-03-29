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
    path('product_unlist/<int:p_id>/', views.product_list_unlist, name='product_unlist'),
    path('product_edit/<int:p_id>', views.prod_edit, name='product_edit'),
    path('category_list', views.category_list, name='category_list'),
    path('add_category/', views.add_category, name='add_category'),
    path('category_unlist/<int:c_id>/', views.category_list_unlist, name='category_unlist'),
    path('add_subcat/', views.add_subcat, name='add_subcat'),
    path('subcategory_list/', views.subcategory_list, name='subcategory_list'),
    path('category_edit/<int:c_id>', views.edit_category, name='category_edit'),
]