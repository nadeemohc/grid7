from django.contrib import admin
<<<<<<< HEAD

=======
# from django_allauth import sites
>>>>>>> main
from accounts.models import User

# Register your models here.

class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'first_name', 'last_name', 'email', 'verified']

admin.site.register(User,UserAdmin)