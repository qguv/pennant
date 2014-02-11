from django.db import models

# Create your models here.
class PCourse(models.Model):
    pcourse_crn = models.IntegerField()

    def __str__(self):
        return str(self.pcourse_crn)
