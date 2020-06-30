from django.db import models
from django.core.validators import validate_email, validate_ipv46_address

# Create your models here.


class User(models.Model):
    email = models.EmailField(max_length=50, validators=[validate_email])
    password = models.CharField(max_length=50)

    def __str__(self):
        return self.email


LEVEL_CHOICES = [
    ('critical', 'critical.'),
    ('debug', 'debug'),
    ('error', 'error'),
    ('warning', 'warning'),
    ('information', 'info'),
]


class ErrorLog(models.Model):
    description = models.CharField(max_length=100)
    details = models.TextField()
    origin = models.GenericIPAddressField(validators=[validate_ipv46_address])
    date = models.DateTimeField()
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
