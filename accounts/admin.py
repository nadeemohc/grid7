from django.contrib import admin

# from django_allauth import sites
from accounts.models import User, Address, Profile

# Register your models here.

class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'first_name', 'last_name', 'email', 'verified']

admin.site.register(User,UserAdmin)

class AddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'street_address', 'city', 'state', 'postal_code', 'country', 'is_default']
admin.site.register(Address, AddressAdmin)

class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'dp_img', 'bio']
admin.site.register(Profile, ProfileAdmin)
