from django.db import models
from django.utils.safestring import mark_safe
from accounts.models import User
# Create your models here.

def user_directory_path(instance, filename):
    if instance.user and instance.user.id:
        return 'user_{0}/{1}'.format(instance.user.id, filename)
    else:
        # Handle the case when user or user.id is None
        return 'user_unknown/{0}'.format(filename)

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
    parent_category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, related_name="subcategories", db_column='cid')

    def __str__(self):
        return self.sub_name

class Product(models.Model):    
    p_id = models.BigAutoField(unique = True, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null = True)
    category = models.ForeignKey(Category, on_delete = models.CASCADE,null = True, related_name ="category")
    sub_category = models.ForeignKey(Subcategory, on_delete = models.CASCADE,null = True, related_name ="sub_category")
    title = models.CharField(max_length = 100,default = "product")
    image = models.ImageField(upload_to=user_directory_path, default = "product.jpg")
    description = models.TextField(null =True, blank =True, default = "This is the product")
    
    price = models.DecimalField(max_digits =10, decimal_places =2, default = 1.99 )
    old_price = models.DecimalField(max_digits =10, decimal_places =2, default = 2.99)
    stock = models.IntegerField(default=1)
    specifications = models.TextField(null =True, blank =True)
    # tags = models.ForeignKey(Tags, on_delete = models.SET_NULL, null =True)
    
    
    
    status = models.BooleanField(default=True)
    in_stock = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    latest = models.BooleanField(default=False)  
    related = models.ManyToManyField('self',blank=True)

    #   sku = models.BigIntegerField(unique =True)
    date = models.DateTimeField(auto_now_add =True)
    updated = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "Products"
        
    def product_image(self):
        return mark_safe('<img src= "%s" width="50" height= "50" />' % (self.image.url))
    
    def __str__(self):
        return self.title
        
    def get_percentage(self):
        new_price = (self.price /self.old_price) * 100
        return new_price
    
class ProductImages(models.Model):
  Images = models.ImageField(upload_to='product-images', default = "product.jpg")
  product = models.ForeignKey(Product, related_name="p_images", on_delete = models.SET_NULL,null =True)
  date = models.DateField(auto_now_add =True)