from django.db import models

# Create your models here.


class BoxUser(models.Model):
    access_token = models.TextField()
    refresh_token = models.TextField()
    csrf_token = models.TextField()
    unique_id = models.TextField()
