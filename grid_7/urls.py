from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

handler404 = 'store.views.handler404'


urlpatterns = [
    path('admin/', admin.site.urls),

    # Installed Apps
    path('', include('accounts.urls')),
    path('', include('store.urls')),
    path('', include('cust_admin.urls')),
    path('', include('cust_auth_admin.urls')),
    path('', include('user_cart.urls')),

    # allauth
    path('accounts/', include('allauth.urls', )),
    path('accounts/', include('allauth.socialaccount.urls')),
    path('home', TemplateView.as_view(template_name='dashboard/home.html'), name='home'),
    
    # Password Reset
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='account/pass_reset_form.html'), name='password_reset'),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(template_name='account/pass_reset_done.html'), name='password_reset_done'),
    path('password_reset_confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='account/pass_reset_confirm.html'), name='password_reset_confirm'),
    path('password_reset_complete/', auth_views.PasswordResetCompleteView.as_view(template_name='account/pass_reset_complete.html'), name='password_reset_complete'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)