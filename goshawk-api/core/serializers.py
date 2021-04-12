from rest_framework import serializers

from core.models import Collection, Reporter, List, Record


class CollectionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Collection
        fields = ['acronym', 'name', 'description', 'default_ttl']


class ReporterSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Reporter
        fields = [ "collection", "name", "active" ]


class ListSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = List
        fields = [ "name", "reporter", "regex", "active" ]


class RecordSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Record
        fields = ["value", "policy", "reporter", "list", "reason", "created_at", "expires_at", "active"]

    reporter = serializers.SlugRelatedField(
        queryset=Reporter.objects.all(), slug_field='name')

    list = serializers.SlugRelatedField(
        queryset=List.objects.all(), slug_field='name')
