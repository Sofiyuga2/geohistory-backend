from rest_framework import serializers

from .models import *


class PioneerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pioneer
        fields = "__all__"


class DiscoverySerializer(serializers.ModelSerializer):
    pioneers = PioneerSerializer(read_only=True, many=True)

    class Meta:
        model = Discovery
        fields = "__all__"

