from rest_framework import serializers
from seguranca_publica.models import Penal

class PenalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Penal
        fields = '__all__'