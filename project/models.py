from django.db      import models

from user.models    import User

class Category(models.Model):
    name = models.CharField(max_length=100)
    name = models.CharField(max_length=10)

    class Meta:
        db_table = 'categories'

class Project(models.Model):
    user             = models.ForeignKey('user.User', on_delete=models.CASCADE)
    category         = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True)
    name             = models.CharField(max_length=200)
    opening_date     = models.DateTimeField()
    closing_date     = models.DateTimeField()
    total_supporters = models.IntegerField()
    created_at       = models.DateTimeField(auto_now_add=True)
    updated_at       = models.DateTimeField(auto_now=True)
    achieved_rate    = models.DecimalField(max_digits=10, decimal_places=2)
    total_price      = models.DecimalField(max_digits=15, decimal_places=2)
    thumbnail_url    = models.URLField(max_length=2000)
    goal_amount      = models.DecimalField(max_digits=15, decimal_places=2)
    summary          = models.CharField(max_length=500)

    class Meta:
        db_table = 'projects'

class Gift(models.Model):
    project       = models.ForeignKey('Project', on_delete=models.CASCADE)
    name          = models.CharField(max_length=100)
    price         = models.DecimalField(max_digits=15, decimal_places=2)
    quantity_sold = models.IntegerField()
    stock         = models.IntegerField()

    class Meta:
        db_table = 'gifts'

class Community(models.Model):
    user       = models.ForeignKey('user.User', on_delete=models.SET_NULL, null=True)
    project    = models.ForeignKey('Project', on_delete=models.CASCADE)
    parent     = models.ForeignKey('self', on_delete=models.CASCADE)
    comment    = models.CharField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'communities'

class Story(models.Model):
    project = models.ForeignKey('Project', on_delete=models.CASCADE)
    content = models.TextField()

    class Meta:
        db_table = 'stories'

class Like(models.Model):
    project = models.ForeignKey('Project', on_delete=models.CASCADE)
    user    = models.ForeignKey('user.User', on_delete=models.CASCADE)

    class Meta:
        db_table = 'likes'
