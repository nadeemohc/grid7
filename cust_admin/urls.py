from django.urls import path
from cust_admin import views

app_name = 'cust_admin'

urlpatterns = [
    path('admin_dashboard/', views.dashboard, name='admin_dashboard'),
    path('user_list/', views.user_list, name='user_list'),
]