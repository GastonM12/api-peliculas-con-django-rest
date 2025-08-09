
from drf_yasg.utils import swagger_auto_schema
from movie.models import Movies
from movie.serializers import Movie_serializer,MovieModelSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

class MoviesView(APIView):
    def get(self,request):
        movies = Movies.objects.all()
        serializer = MovieModelSerializer(movies, many = True)
       
        return Response(serializer.data,status=200)
    @swagger_auto_schema(request_body=MovieModelSerializer)
    def post(self,request):
         serializer = MovieModelSerializer(data = request.data)
         if serializer.is_valid():
           serializer.save()
           return Response(serializer.data,status=201)
         return Response(serializer.errors,status=400)
    @swagger_auto_schema(request_body=Movie_serializer)
    def put(self,request,pk=None):
     try:
        movie=Movies.objects.get(id=pk)
        serializer = Movie_serializer(movie,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=200)
        return Response(serializer.errors,status=400)
     except:
        return Response("Not found",status=404)



# @swagger_auto_schema(method="POST",request_body=MovieModelSerializer)
# @api_view(["GET","POST"])
# def get_movies(request):
#     if request.method == "GET":
#         movies = Movies.objects.all()
#         serializer = MovieModelSerializer(movies, many = True)
       
#         return Response(serializer.data,status=200)
    
#     if request.method == "POST":
#        serializer = MovieModelSerializer(data = request.data)
#        if serializer.is_valid():
#            serializer.save()
#            return Response(serializer.data,status=201)
#        return Response(serializer.errors,status=400)
#     return Response({},status=405)

# @swagger_auto_schema(method="PUT",request_body=Movie_serializer)
# @api_view(["PUT"])
# def update_movie(request,pk):
#     try:
#         movie=Movies.objects.get(id=pk)
#         serializer = Movie_serializer(movie,data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data,status=200)
#         return Response(serializer.errors,status=400)
#     except:
#         return Response("Not found",status=404)
