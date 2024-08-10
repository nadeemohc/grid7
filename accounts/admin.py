from django.contrib import admin

# from django_allauth import sites
from accounts.models import*

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

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance', 'points')

@admin.register(Referral)
class ReferralAdmin(admin.ModelAdmin):
    list_display = ('referrer', 'referred', 'referral_code', 'date_created')
@admin.register(WalletHistory)
class ReferralAdmin(admin.ModelAdmin):
    list_display = ('wallet', 'transaction_type', 'created_at', 'amount', 'reason')