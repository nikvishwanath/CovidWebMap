from django.db import models
import geocoder

# Create your models here.


class Data(models.Model):
    country = models.CharField(max_length=100, null=True)
    cases = models.PositiveIntegerField(null=True)
    deaths = models.PositiveIntegerField(null=True)
    date_updated = models.CharField(max_length=20, null=True)
   
    class Meta:
        verbose_name_plural = 'Data'

    def __str__(self):
        return self.country