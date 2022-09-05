from django.db import models
from django.contrib.auth.models import User

class TitleModel(models.Model):
    """A class to store titles that the user will add to their list."""

    id = models.CharField(primary_key=True, max_length=20)
    title_name = models.CharField(max_length=100)
    image_url = models.CharField(max_length=1000)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.id