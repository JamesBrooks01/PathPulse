from django.db import models
from django.contrib.postgres.fields import ArrayField

# Create your models here.

class User(models.Model):
    user_email = models.EmailField(max_length=200)
    user_trips = ArrayField(
        ArrayField(
            models.CharField(max_length=200)
        )
    )

    def __str__(self):
        return self.user_trips