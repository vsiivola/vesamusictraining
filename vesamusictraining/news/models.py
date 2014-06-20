from django.db import models

# Create your models here.
class NewsItem(models.Model):
    title = models.CharField(max_length=200)
    date = models.DateTimeField()
    content = models.CharField(max_length=8000)
    language = models.CharField(max_length=10)

