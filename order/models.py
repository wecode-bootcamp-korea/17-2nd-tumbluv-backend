from django.db          import models

from user.models        import User
from project.models     import Project

class Order(models.Model):
    user           = models.ForeignKey('user.User', on_delete=models.CASCADE)
    gift           = models.ForeignKey('project.Gift', on_delete=models.SET_NULL, null=True)
    recipient      = models.ForeignKey('Recipient', on_delete=models.SET_NULL, null=True)
    card_number    = models.ForeignKey('CardNumber', on_delete=models.SET_NULL, null=True)
    account_number = models.ForeignKey('AccountNumber', on_delete=models.SET_NULL, null=True)
    donation       = models.DecimalField(max_digits=15, decimal_places=2)
    status         = models.ForeignKey('Status', on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = 'orders'

class Recipient(models.Model):
    user         = models.ForeignKey('user.User', on_delete=models.SET_NULL, null=True)
    fullname     = models.CharField(max_length=100)
    address      = models.CharField(max_length=500)
    phone_number = models.CharField(max_length=40)
    post_code    = models.IntegerField(null=True)
    is_defalut   = models.BooleanField(default=False)

    class Meta:
        db_table = 'recipients'

class CardNumber(models.Model):
    user         = models.ForeignKey('user.User', on_delete=models.SET_NULL, null=True)
    card_number  = models.CharField(max_length=16)
    is_defalut   = models.BooleanField(default=False)

    class Meta:
        db_table = 'card_numbers'

class AccountNumber(models.Model):
    user           = models.ForeignKey('user.User', on_delete=models.SET_NULL, null=True)
    account_number = models.CharField(max_length=20)
    is_defalut     = models.BooleanField(default=False)

    class Meta:
        db_table = 'account_numbers'

class Status(models.Model):
    status = models.CharField(max_length=20)

    class Meta:
        db_table = 'statuses'
