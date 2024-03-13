from django.db import models
from django.utils.safestring import mark_safe
# Create your models here.

class Category(models.Model):
    cid = models.BigAutoField(unique=True, primary_key=True)
    cname = models.CharField(max_length = 50)
    image = models.ImageField(upload_to='category',default='category.jpg')
    is_blocked = models.BooleanField(default=False)
    class Meta:
        verbose_name_plural = "Categories"

    def category_image(self):
        if self.image:
            return mark_safe('<img src="%s" width="50" height="50" />' % (self.image.url))
        else:
            return "NO Image Available"

    def __str__(self):
        return self.cname
    
class Subcategory(models.Model):
    sid = models.BigAutoField(unique=True, primary_key = True)
    sub_name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, related_name="subcategories",db_column = 'cid')

    def __str__(self):
        return self.sub_name