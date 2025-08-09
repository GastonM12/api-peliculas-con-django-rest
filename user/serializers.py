from rest_framework import serializers
from user.models import RateMovie


class RateMovieSerializer(serializers.ModelSerializer):
    class Meta:
        model=RateMovie
        fields = ["id","rating","user","movie"]