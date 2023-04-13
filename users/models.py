from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    user_type = models.CharField(max_length=255, default="user")
    gender = models.CharField(max_length=255, default="Male")
    verified_email = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # @property
    def imageURL(self):
        try: 
            url = self.profile_pic.url
        except:
            url = "Sorry no image to see here"
        return url
    
    def __str__(self):
        return self.first_name + ", " + self.last_name
