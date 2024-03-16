from django.db import models
from django.utils.safestring import mark_safe
from accounts.models import User
# Create your models here.

def generic_directory_path(instance,filename):
    model_name = instance.__class__.__name__.lower()

    pk = instance.pid if hasattr(instance,'pid') else None

    if pk:
        return f'{model_name}_{pk}/{filename}'
    else:
        return f'{model_name}_unknown/{filename}'
# def user_directory_path(instance, filename):
#     if instance.user and instance.user.id:
#         return 'user_{0}/{1}'.format(instance.user.id, filename)
#     else:
#         return 'user_unknown/{0}'.format(filename)
# def user_directory_path(instance, filename):
#     # Your logic to determine the upload path based on the user instance
#     pass

class Category(models.Model):
    c_id = models.BigAutoField(unique=True, primary_key=True)
    c_name = models.CharField(max_length = 50, null=True)
    c_image = models.ImageField(upload_to='category',default='category.jpg')
    is_blocked = models.BooleanField(default=False)
    class Meta:
        verbose_name_plural = "Categories"

    def category_image(self):
        if self.c_image:
            return mark_safe('<img src="%s" width="50" height="50" />' % (self.c_image.url))
        else:
            return "No Image Available"


    def __str__(self):
        return self.c_name
    
class Subcategory(models.Model):
    sid = models.BigAutoField(unique=True, primary_key=True)
    sub_name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, related_name="subcategories", db_column='c_id')

    def __str__(self):
        return self.sub_name

class Product(models.Model):    
    p_id = models.BigAutoField(unique=True, primary_key=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, related_name="products")
    sub_category = models.ForeignKey(Subcategory, on_delete=models.CASCADE, null=True, related_name="products")
    title = models.CharField(max_length=100, default="product")
    image = models.ImageField(upload_to=generic_directory_path, default="product.jpg")
    description = models.TextField(null=True, blank=True, default="This is the product")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=1.99)
    old_price = models.DecimalField(max_digits=10, decimal_places=2, default=2.99)
    stock = models.IntegerField(default=1)
    specifications = models.TextField(null=True, blank=True)
    is_blocked = models.BooleanField(default=False)
    status = models.BooleanField(default=True)
    in_stock = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    latest = models.BooleanField(default=False)  
    related = models.ManyToManyField('self', blank=True)
    date = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "Products"
        
    def product_image(self):
        return mark_safe('<img src="%s" width="50" height="50" />' % (self.image.url))
    
    def __str__(self):
        return self.title
        
    def get_percentage(self):
        new_price = (self.price / self.old_price) * 100
        return new_price

# class ProductImages(models.Model):
#     image = models.ImageField(upload_to='generic_directory_path', default="product.jpg")
#     product = models.ForeignKey(Product, related_name="p_images", on_delete=models.SET_NULL, null=True)
#     date = models.DateField(auto_now_add=True)

class ProductImages(models.Model):
    images = models.ImageField(upload_to='product_images',default='product.jpg')
    product = models.ForeignKey(Product,related_name='images', on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
      verbose_name_plural = 'Product Images'