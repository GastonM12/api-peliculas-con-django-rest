from drf_yasg.utils import swagger_auto_schema

from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet

from user.models import RateMovie
from user.serializers import RateMovieSerializer
# Create your views here.


class RateViews(ViewSet):
    serializer_class = RateMovieSerializer

    def list(self,request):
        user_rates=RateMovie.objects.filter(user_id=request.user.id)
        serializer=RateMovieSerializer(user_rates,many=True)
        return Response(serializer.data,status=200)
    
    @swagger_auto_schema(request_body=RateMovieSerializer)
    def create(self,request):
        if request.data("user1") != request.user.id:
          return Response("User doesn't match",status=403)
        
        serializer = RateMovieSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=201)
        return Response(serializer.errors,status=400)