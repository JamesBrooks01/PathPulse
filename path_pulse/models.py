from django.db import models

# Create your models here.

class User(models.Model):
    user_email = models.EmailField(max_length=200)

    def __str__(self):
        return self.user_email
    
class Trip(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    city = models.CharField(max_length=200)
    state = models.CharField(max_length=200)
    country = models.CharField(max_length=200)
    start_date = models.CharField(max_length=200)
    end_date = models.CharField(max_length=200)

    def __str__(self):
        return f"Trip to {self.city}, {self.city}, {self.country}. It starts on {self.start_date} and ends on {self.end_date}"