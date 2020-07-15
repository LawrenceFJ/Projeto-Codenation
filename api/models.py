from django.db import models
from django.core.validators import validate_ipv46_address
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

# Create your models here.
LEVEL_CHOICES = [
    ('critical', 'critical'),
    ('debug', 'debug'),
    ('error', 'error'),
    ('warning', 'warning'),
    ('information', 'info'),
]


class UserManager(BaseUserManager):
    def create_user(self, email, name, password=None, is_admin=False, is_staff=False, is_active=True):
        if not email:
            raise ValueError("User must have an email")
        if not name:
            raise ValueError("User must have a name")
        if not password:
            raise ValueError("User must have a password")

        user = self.model(
            email=self.normalize_email(email)
        )
        user.name = name
        user.set_password(password)  # change password to hash
        user.admin = is_admin
        user.staff = is_staff
        user.active = is_active
        user.save(using=self._db)
        return user

    def create_staffuser(self, email, name, password=None):
        user = self.create_user(
            email,
            name,
            password=password,
            is_staff=True,
        )
        return user

    def create_superuser(self, email, name, password=None):
        user = self.create_user(
            email,
            name,
            password=password,
            is_staff=True,
            is_admin=True,
        )
        return user


class User(AbstractBaseUser):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    active = models.BooleanField(default=True)
    staff = models.BooleanField(default=False)  # a admin user; non super-user
    admin = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    objects = UserManager()

    def get_full_name(self):
        # The user is identified by their email address
        return self.email

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    def __str__(self):
        return self.email

    @staticmethod
    def has_perm(perm, obj=None):
        # "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    @staticmethod
    def has_module_perms(app_label):
        # "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        # "Is the user a member of staff?"
        return self.staff

    @property
    def is_admin(self):
        # "Is the user a admin member?"
        return self.admin

    @property
    def is_active(self):
        # "Is the user active?"
        return self.active


class ErrorLog(models.Model):
    description = models.CharField(max_length=100)
    details = models.TextField()
    origin = models.GenericIPAddressField(validators=[validate_ipv46_address])
    date = models.DateTimeField()
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
