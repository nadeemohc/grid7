from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission
from django.utils import timezone
import random
import string

class UserManager(BaseUserManager):
    def create_user(self, first_name, last_name, username, email, password=None, referral_code=None):
        if not email:
            raise ValueError('User must have an email address')
        if not username:
            raise ValueError('User must have a username')
        
        # Generate unique referral code if not provided
        if not referral_code:
            referral_code = self.generate_unique_referral_code()
        
        user = self.model(
            email=self.normalize_email(email),
            username=username,
            first_name=first_name,
            last_name=last_name,
            referral_code=referral_code
        )
        user.set_password(password)
        user.save(using=self._db)
        
        # Create an empty wallet for the user
        Wallet.objects.create(user=user)
        
        return user
    
    def generate_unique_referral_code(self):
        length = 8
        while True:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
            print(f"Generated referral code: {code}")  # Debugging line
            if not User.objects.filter(referral_code=code).exists():
                return code


    
    def create_superuser(self, first_name, last_name, username, email, password=None):
        user = self.create_user(
            email=self.normalize_email(email),
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
        user.is_admin = True
        user.is_active = True
        user.is_staff = True
        user.is_superadmin = True
        user.save(using=self._db)
        return user
    
    def generate_unique_referral_code(self):
        length = 8
        while True:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
            if not User.objects.filter(referral_code=code).exists():
                return code


class User(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    verified = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    referral_code = models.CharField(max_length=50, unique=True, null=True, blank=True)
    referred_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='referrals')

    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    is_superadmin = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    objects = UserManager()

    groups = models.ManyToManyField(Group, blank=True, related_name='account_user_groups')
    user_permissions = models.ManyToManyField(Permission, blank=True, related_name='account_user_permissions')

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    dp_img = models.ImageField(upload_to='image', blank=True, null=True)
    bio = models.CharField(max_length=220, blank=True, null=True)

    def __str__(self):
        return f"Profile of {self.user.username}"

class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    street_address = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.street_address}, {self.city}, {self.state} - {self.postal_code}"

class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name_plural = 'Wallet'

    def __str__(self):
        return self.user.email

class WalletHistory(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    transaction_type = models.CharField(null=True, blank=True, max_length=20)
    created_at = models.DateTimeField(default=timezone.now)
    amount = models.IntegerField(null=True)
    reason = models.CharField(null=True, blank=True, max_length=200)


class Referral(models.Model):
    referrer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_referrals')
    referred = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_referrals')
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.referrer.username} referred {self.referred.username}"
