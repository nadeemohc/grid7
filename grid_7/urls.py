from django.contrib import admin
from django.urls import path, include
<<<<<<< HEAD
=======
from django.views.generic import TemplateView
>>>>>>> main

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('', include('store.urls')),
    path('accounts/', include('allauth.urls')),
    path('accounts/', include('allauth.socialaccount.urls')),
<<<<<<< HEAD
=======
    # path('accounts/google/login/' TemplateView.as_view(template_name='')))
    path('home', TemplateView.as_view(template_name='dashboard/home.html'), name='home')
>>>>>>> main
]
