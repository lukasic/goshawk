from rest_framework import serializers

from core.models import Collection, Reporter, List, Record


class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ['acronym', 'name', 'description', 'default_ttl']


class ReporterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reporter
        fields = [ "id", "collection", "name", "active" ]
        lookup_field = "name"

class ListSerializer(serializers.ModelSerializer):
    class Meta:
        model = List
        fields = [ "id", "name", "reporter", "regex", "active" ]


class RecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Record
        fields = ["value", "policy", "reporter", "list", "reason", "created_at", "expires_at", "active"]

