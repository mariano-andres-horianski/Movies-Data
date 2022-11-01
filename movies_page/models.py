from email.policy import default
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
class TitleModel(models.Model):
    """
    A table to cache added titles, in order to not retrieve them from the API if they are already on this table.
    The idea is that I later modify the delete function for AddedTitleModel so if this title is not stored in any list
    It's removed and thus it's mutable data will not be stored.

    Caching a title's data is needed as I only have 100 daily API requests, 
    which is a problem when doing tests that require me to reload the titles-list page, 
    since it runs multiple requests every time.
    
    Redis cache doesn't help if the server is closed or if the lifetime for the data stored ends.
    """

    id = models.CharField(primary_key=True, max_length=20)
    title_data = models.TextField()

    def __str__(self):
        return self.id
    

class AddedTitleModel(models.Model):
    """A class to store titles that the user will add to their list and rate."""

    id = models.AutoField(primary_key=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.ForeignKey(TitleModel, on_delete=models.CASCADE)


    def __str__(self):
        return str(self.title.id)
