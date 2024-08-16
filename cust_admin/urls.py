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

    # coupon functionalities
    path('add-coupon/', views.add_coupon, name='add_coupon'),
    path('coupons/', views.coupon_list, name='coupon_list'),
    path('edit-coupon/<int:coupon_id>/', views.edit_coupon, name='edit_coupon'),
    path('delete-coupon/<int:coupon_id>/', views.delete_coupon, name='delete_coupon'),
    # category offer functionalities
    path('category_offer/', views.category_offer_list, name='category_offer_list'),
    path('category_offer/add/', views.add_category_offer, name='add_category_offer'),
    path('category_offer/edit/<int:offer_id>/', views.edit_category_offer, name='edit_category_offer'),
    path('category_offer/delete/<int:offer_id>/', views.delete_category_offer, name='delete_category_offer'),
    # product offer functionalities
    path('product_offer/', views.product_offer_list, name='product_offer_list'),
    path('product_offer/add/', views.add_product_offer, name='add_product_offer'),
    path('product_offer/edit/<int:offer_id>/', views.edit_product_offer, name='edit_product_offer'),
    path('product_offer/delete/<int:offer_id>/', views.delete_product_offer, name='delete_product_offer'),
    # sales statistics
    path('sales-report/', views.sales_report, name='sales_report'),
    path('daily-report/', views.daily_report, name='daily_report'),
    path('weekly-report/', views.weekly_report, name='weekly_report'),
    path('monthly-report/', views.monthly_report, name='monthly_report'),
    # pdf / excel export
    path('export-pdf/<str:report_type>/', views.export_to_pdf, name='export_pdf'),
    path('export-excel/<str:report_type>/', views.export_to_excel, name='export_excel'),
    # graph statistics
    path('get_daily_sales_data/', views.get_daily_sales_data, name='get_daily_sales_data'),
    path('get_monthly_sales_data/', views.get_monthly_sales_data, name='get_monthly_sales_data'),
    path('get_yearly_sales_data/', views.get_yearly_sales_data, name='get_yearly_sales_data'),
    path('get_order_status_data/', views.get_order_status_data, name='get_order_status_data'),
    path('sales_statistics/', views.sales_statistics, name='sales_statistics'),
    path('export-custom-sales-report/', views.sales_report, name='export_custom_sales_report'),
    # Best selling 
    path('best-selling-products/', views.best_selling_products, name='best_selling_products'),
    # path('best-selling-subcategories/', views.best_selling_subcategories, name='best_selling_subcategories'),
    # path('best-selling-brands/', views.best_selling_brands, name='best_selling_brands'),
]