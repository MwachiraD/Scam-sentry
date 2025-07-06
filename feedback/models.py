from django.db import models
from django.db import models

class Feedback(models.Model):
    name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    message = models.TextField()

    def __str__(self):
        return f"Feedback from {self.name or 'Anonymous'}"

# Create your models here.
