from django.contrib import admin

# from django_allauth import sites
from store.models import Category, Product

# Register your models here.

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['c_id', 'c_name', 'c_image', 'is_blocked']


admin.site.register(Category, CategoryAdmin)

class ProductAdmin(admin.ModelAdmin):
    list_display = ['p_id', 'user', 'category', 'sub_category', 'title', 'image', 'description', 'price', 'old_price', 'stock','specifications']

admin.site.register(Product, ProductAdmin)