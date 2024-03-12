from django.urls import path
from cust_admin import views

app_name = 'cust_admin'

urlpatterns = [
    path('admin_home/', views.dashboard, name='admin_home'),
]