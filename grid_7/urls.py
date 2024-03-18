from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

handler404 = 'store.views.handler404'


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('', include('store.urls')),
    path('', include('cust_admin.urls')),
    path('', include('cust_auth_admin.urls')),
    path('accounts/', include('allauth.urls')),
    path('accounts/', include('allauth.socialaccount.urls')),
    # path('accounts/google/login/' TemplateView.as_view(template_name='')))
    path('home', TemplateView.as_view(template_name='dashboard/home.html'), name='home'),
    # path('login/', auth_views.LoginView.as_view(), name='login'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)