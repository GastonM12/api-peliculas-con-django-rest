from django.urls import path
from movie.views import MoviesView

app_name = 'movie'

urlpatterns = [
  #path("",get_movies,name="movies") , 
  #  path("<int:pk>",update_movie,name="movies") 

    path("", MoviesView.as_view(), name="movies"),         # GET lista y POST crea
    path("<int:pk>/", MoviesView.as_view(), name="movie-detail"),  # PUT actualiza

]