from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission

# ----------------------------Custom User Manager----------------------------------
class CustomUserManager(BaseUserManager):
    def create_user(self, email, full_name='', password=None, role='Viewer', status='active'):
        """
        Create and save a regular user.
        """
        if not email:
            raise ValueError('Users must have an email address')
        email = self.normalize_email(email)
        user = self.model(email=email, full_name=full_name, role=role, status=status)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, full_name='', password=None):
        """
        Create and save a superuser (Admin).
        """
        user = self.create_user(email=email, full_name=full_name, password=password, role='Admin', status='active')
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user

# ----------------------------Custom User Model-----------------------------------
class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('Admin', 'Admin'),
        ('Employee', 'Employee'),
        ('Viewer', 'Viewer'),
    ]
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    ]

    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='Viewer')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    date_joined = models.DateTimeField(auto_now_add=True)
    
    # Required for Django admin
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.full_name or self.email
