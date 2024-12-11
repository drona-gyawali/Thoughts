from math import fabs
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.db import models
import os
from django.db.models import UniqueConstraint
"""
This models.py is consist of the operation related to the database.

Expected: 
       You will see the crud operations.
       You will see some helper function.
       You will see some sever-side logic.
       You will see Meta-class defined for some models.
"""

# models that take the title and desc.
class Content(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    title = models.CharField(max_length=150, null=False,blank =False)
    description = models.TextField(null= False, blank = False)
    email= models.EmailField(unique=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f'Title: {self.title}'

class Profile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    image = models.ImageField(upload_to ='profile_images/%Y/%m/%d/',default = 'profile_images\2024\12\10\default.jpg',null =True, blank = True)

    def __str__(self):
        return f"{self.user.username}'s Profile"



#models responsible for like activity.
class Like(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE,null=False,blank=False)
    content = models.ForeignKey(Content, on_delete=models.CASCADE, related_name='like')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            UniqueConstraint(fields=['content','user'], name = 'unique_user_like_post')
        ]


    
#model responsible for comment activity.
class Comment(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    content = models.ForeignKey(Content, on_delete = models. CASCADE)
    comment = models.CharField(max_length = 500)
    created_at = models.DateTimeField(auto_now_add = True)


    def __str__(self) -> str:
        return f'Comment by {self.user.username} on {self.content.title}'





