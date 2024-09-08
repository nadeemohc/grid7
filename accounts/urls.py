from django.urls import path
from accounts import views

app_name = 'accounts'

urlpatterns = [
    #  Authentication functionalities 
    path('login/', views.perform_login, name='login'),
    path('logout/', views.perform_logout, name='logout'),
    path('signup/', views.perform_signup, name='perform_signup'),

    #  Otp functionalities
    path('otp_verification/', views.otp_verification, name='otp_verification'),
    path('otp_verification_login/', views.otp_verification_login, name='otp_verification_login'),
    path('resend_otp/', views.resend_otp, name='resend_otp'),
    
]
