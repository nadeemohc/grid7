from django.urls import path
from accounts import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.perform_login, name='login'),
    path('logout/', views.perform_logout, name='logout'),
    path('signup/', views.perform_signup, name='signup'),
    path('otp_verification/', views.otp_verification, name='otp_verification'),
]
