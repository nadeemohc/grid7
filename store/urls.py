from django.urls import path
from store import views

app_name = 'store'

urlpatterns = [
    path('', views.home, name='home'),

    #  Related to Products 
    path('search/', views.search_and_filter, name='search_and_filter'),
    path('product_list/', views.list_prod, name='product_list'),
    path('product_list_by_category/<int:category_cid>/',views.product_list_by_category,name = 'product_list_by_category'),
    path('product_view/<int:product_pid>/', views.product_detailed_view, name='product_view'),
    
    #  Related to wishlist
    path('get_wishlist_count/', views.get_wishlist_count, name='get_wishlist_count'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('add_wishlist/<int:product_pid>/', views.add_wishlist, name='add_to_wishlist'),
    path('delete_wishlist/<int:pk>/', views.delete_wishlist, name='delete_wishlist'),
    
    #  Related to user profile
    path('user_profile/', views.user_profile, name='user_profile'),
    path('order/<int:order_id>/', views.user_order_detail, name='user_order_detail'),
    path('order/return/<int:order_id>/', views.order_return, name='order_return'),
    path('order/cancel/<int:order_id>/', views.order_cancel, name='order_cancel'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),

    #  Related to address in user profile page
    path('add_address/', views.add_address, name='add_address'),
    path('edit_address/<int:address_id>/', views.edit_address, name='edit_address'),
    path('delete_address/<int:pk>', views.delete_address, name='delete_address'),

    # Related to password change in user profile page
    path('change_password/', views.change_password, name='change_password'),

    # Viewing shop
    path('shop/', views.shop, name='shop'),
    path('shop/<int:category_id>/', views.shop, name='shop_by_category'),
    path('get_price/<int:size_id>/', views.get_price, name='get_price'),

    # viewing coupons
    path('list_coupons/', views.list_coupon, name='list_coupon'),
    
    # path('send-referral-code/', views.send_referral_code, name='send_referral_code'),
]
