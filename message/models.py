from django.db import models

from project.models     import Project
from user.models        import User

class Message(models.Model):
    project    = models.ForeignKey('project.Project', on_delete=models.SET_NULL, null=True)
    user       = models.ForeignKey('user.User', on_delete=models.CASCADE)
    text       = models.CharField(max_length=2000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status     = models.BooleanField(default=0)

    class Meta:
        db_table = 'messages'
