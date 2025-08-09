from rest_framework import serializers
from movie.models import Movies

class Movie_serializer(serializers.Serializer):
    id = serializers.IntegerField()
    titulo = serializers.CharField(max_length = 200)
    release_date= serializers.DateField()
    duration = serializers.IntegerField()
    synopsis = serializers.CharField()


    def create(self, validated_data):
        validated_data.pop("id")
        movie = Movies.objects.create(**validated_data)
        return movie
    
    def update(self,instance,validated_data):
        instance.titulo = validated_data.get("titulo",instance.titulo)
        instance.release_date = validated_data.get("release_date",instance.release_date)
        instance.duration = validated_data.get("duration",instance.duration)
        instance.synopsis = validated_data.get("synopsis",instance.synopsis)

        instance.save()
        return instance

class MovieModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movies
        fields= ["id","titulo","release_date","duration","synopsis"]