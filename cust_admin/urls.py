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
]