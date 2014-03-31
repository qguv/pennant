from django.db import models

# Create your models here.
class PCourse(models.Model):
    #isOpen = models.BooleanField()
    pcourse_crn = models.IntegerField()
    #department = models.TextField()
    #level = models.TextField()
    #section = models.TextField()
    title = models.TextField()
    #professor = models.TextField()
    #creditHours = models.TextField()
    #attributes = models.TextField()
    #gers = models.TextField()
    #days = models.TextField()
    #projectedE = models.IntegerField()
    #currentE = models.IntegerField()
    #seats = models.IntegerField()
    

    def __str__(self):
        return str(self.title)
