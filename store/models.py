from django.db import models
from django.utils.safestring import mark_safe
from django.utils import timezone
from accounts.models import User, Address
# Create your models here.

class Size(models.Model):
    sizze = [
        ('S', 'Small'),
        ('M', 'Medium'),
        ('L', 'Large'),
        ('XL', 'Extra Large'),
        ('XXL', 'Extra Extra Large'),
    ]
    size = models.CharField(max_length=50, choices=sizze)
    price_increment = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return self.size

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
    shipping = models.TextField(null =True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=1.99)
    old_price = models.DecimalField(max_digits=10, decimal_places=2, default=2.99)
    stock = models.IntegerField(default=1)
    specifications = models.TextField(null=True, blank=True)
    size = models.ManyToManyField(Size, blank= True)
    is_blocked = models.BooleanField(default=False)
    status = models.BooleanField(default=True)
    in_stock = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    latest = models.BooleanField(default=False)  
    popular = models.BooleanField(default=True)
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

class ProductImages(models.Model):
    images = models.ImageField(upload_to='product_images',default='product.jpg')
    product = models.ForeignKey(Product,related_name='images', on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
      verbose_name_plural = 'Product Images'

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_item_count(self):
        return self.items.count()  # Use the related name 'items' instead of 'cartitem_set'

    def __str__(self):
        return f"Cart for {self.user.username}"


class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    size = models.CharField(max_length=50)  # Add size field
    is_deleted = models.BooleanField(default=False)

    def product_image(self):
        # Assuming you want to retrieve the first image of the product
        first_image = self.product.p_images.first()
        if first_image:
            return first_image.Images.url
        return None

    def __str__(self):
        return f"{self.quantity} x {self.product.title} in {self.cart}"


class Payments(models.Model):
    payment_choices=(
        ('COD','COD'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=100)
    payment_method = models.CharField(max_length=100,choices=payment_choices)
    amount_paid = models.CharField(max_length=100)
    status = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.first_name
        

class CartOrder(models.Model):
    STATUS =(
        ('New','New'),
        ('Paid','Paid'),
        ('Shipped','Shipped'),
        ('Conformed','Conformed'),
        ('Pending','Pending'),
        ('Delivered','Delivered'),
        ('Cancelled','Cancelled'),
        ('Return','Return')
    )
    user=models.ForeignKey(User,on_delete=models.SET_NULL,null=True)
    payment=models.ForeignKey(Payments,on_delete=models.SET_NULL,blank=True,null=True)
    order_number = models.CharField(max_length=20,default=None)
    order_total = models.FloatField(null=True, blank=True)
    status=models.CharField(max_length=10, choices=STATUS, default='New')
    ip =  models.CharField(blank=True,max_length=20)
    is_ordered=models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now, editable=True)
    updated_at=models.DateTimeField(auto_now=True)
    selected_address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        verbose_name_plural = "Cart Order"
    
    def __str__(self):
        return self.order_number


class ProductOrder(models.Model):
    order=models.ForeignKey(CartOrder,on_delete=models.SET_NULL, null=True)
    payment = models.ForeignKey(Payments,on_delete=models.SET_NULL,blank=True,null=True)
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity=models.IntegerField()
    product_price=models.FloatField(default=0)
    ordered=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    variations = models.ForeignKey(Size, on_delete=models.CASCADE, null=True)
    def __str__(self):
        return self.product.product_name

