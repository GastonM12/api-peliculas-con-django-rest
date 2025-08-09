from django.db import models
from django.contrib.auth.models import AbstractUser

from movie.models import Movies
# Create your models here.



#De esta manera creamos la aplicacion para crear usuarios para que se puedan loguear en nuestra app
class CustomUser(AbstractUser):
    birthdate = models.DateField(null=True,blank=True)
    
    def __str__(self):
        return self.username
    
class RateMovie(models.Model):
    user=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    movie=models.ForeignKey(Movies,on_delete=models.CASCADE)    
    rating = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ["user","movie"]