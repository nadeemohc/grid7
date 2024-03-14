from django.contrib import admin

# from django_allauth import sites
from store.models import Category

# Register your models here.

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['c_id', 'c_name', 'c_image', 'is_blocked']

admin.site.register(Category, CategoryAdmin)