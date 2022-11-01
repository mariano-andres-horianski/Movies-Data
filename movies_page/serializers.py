from rest_framework import serializers
from .models import AddedTitleModel
class AddedTitleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = AddedTitleModel