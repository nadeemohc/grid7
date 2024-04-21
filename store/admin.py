from django.contrib import admin

# from django_allauth import sites
from store.models import Category, Product, Subcategory, ProductImages, Size

# Register your models here.

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['c_id', 'c_name', 'c_image', 'is_blocked']


admin.site.register(Category, CategoryAdmin)

class ProductAdmin(admin.ModelAdmin):
    list_display = ['p_id', 'category', 'sub_category', 'title', 'image', 'description', 'price', 'old_price', 'stock','specifications']

admin.site.register(Product, ProductAdmin)

class SubcategoryAdmin(admin.ModelAdmin):
    list_display = ['sid', 'sub_name', 'category']

admin.site.register(Subcategory, SubcategoryAdmin)

class ProductImagesAdmin(admin.ModelAdmin):
    list_display = ['id', 'product_id', 'images']
    
admin.site.register(ProductImages, ProductImagesAdmin)

admin.site.register(Size)