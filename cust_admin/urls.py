from django.urls import path
from cust_admin import views

app_name = 'cust_admin'

urlpatterns = [
    path('admin_dashboard/', views.dashboard, name='admin_dashboard'),

    # User functoinalities
    path('user_view/<str:username>/', views.user_view, name='user_view'),
    path('user_list/', views.user_list, name='user_list'),
    path('user_block/<str:username>/', views.user_block_unblock, name='user_block'),

    # Product functionalities 
    path('add_product/', views.add_product, name='add_product'),
    path('prod_list/', views.prod_list, name='prod_list'),
    path('product_unlist/<int:p_id>/', views.product_list_unlist, name='product_unlist'),
    path('product_edit/<int:p_id>', views.prod_edit, name='product_edit'),
    path('prod_variant_assign/', views.prod_variant_assign, name='prod_variant_assign'),
    path('prod_variant_edit/<int:pk>/', views.prod_variant_edit, name='prod_variant_edit'),
    path('prod_catalogue/', views.prod_catalogue_list, name='prod_catalogue'),
    path('catalogue_unlist/<int:pk>/', views.catalogue_list_unlist, name='catalogue_unlist'),
    
    # Category functionalities
    path('category_list', views.category_list, name='category_list'),
    path('add_category/', views.add_category, name='add_category'),
    path('category_unlist/<int:c_id>/', views.category_list_unlist, name='category_unlist'),
    path('category_edit/<int:c_id>', views.edit_category, name='category_edit'),

    # subcategory functionalities
    path('add_subcat/', views.add_subcat, name='add_subcat'),
    path('subcategory_list/', views.subcategory_list, name='subcategory_list'),

    # Variant functionalities
    path('add_variant', views.add_variant, name='add_variant'),
    path('list_variant/', views.list_variant, name='list_variant'),
    path('edit_variant/<int:id>/', views.edit_variant, name='edit_variant'),

    # Order functionalities
    path('orders/', views.list_order, name='list_order'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('orders/<int:order_id>/update_status/', views.order_update_status, name='order_update_status'),
]
