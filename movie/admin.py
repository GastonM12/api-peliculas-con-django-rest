from django.contrib import admin

# Register your models here.
from movie.models import Movies

class MovieAdmin(admin.ModelAdmin):
    list_display=("titulo","duration")


admin.site.register(Movies,MovieAdmin)
