from django.contrib import admin
from django.urls import path
from cust_auth_admin import views

app_name = 'admin_auth'

urlpatterns = [
    # Authentication Functionalities
    path('admin_login/', views.admin_login, name = 'admin_login'),
    path('admin_logout/', views.admin_logout, name='admin_logout'),
]