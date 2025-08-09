from django.db import models

# Create your models here.
class Movies(models.Model):
    titulo=models.CharField(max_length=200)
    release_date=models.DateField()
    duration=models.PositiveIntegerField()
    synopsis = models.TextField()


    def __str__(self):
        return f"{self.id}-{self.titulo}"