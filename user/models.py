from django.db import models

class User(models.Model):
    fullname         = models.CharField(max_length=40)
    email            = models.CharField(max_length=200, unique=True)
    password         = models.CharField(max_length=200, null=True)
    profile_image    = models.URLField(max_length=2000, null=True)
    user_description = models.CharField(max_length=1000, null=True)
    phone_number     = models.CharField(max_length=40, null=True)

    class Meta:
        db_table = 'users'

class Verification(models.Model):
    code       = models.CharField(max_length=6)
    email      = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'verifications'
