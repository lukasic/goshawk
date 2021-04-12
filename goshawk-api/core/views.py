from django.shortcuts import render

from rest_framework import viewsets
from rest_framework import permissions
from rest_framework import generics

from django_filters.rest_framework import DjangoFilterBackend

from core.models import Collection, Reporter, List, Record
from core.serializers import CollectionSerializer, ReporterSerializer, ListSerializer, RecordSerializer

class CollectionViewSet(viewsets.ModelViewSet):
    queryset = Collection.objects.all().order_by('acronym')
    serializer_class = CollectionSerializer
#    permission_classes = [permissions.IsAuthenticated]

class ReporterViewSet(viewsets.ModelViewSet):
    queryset = Reporter.objects.all()
    serializer_class = ReporterSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = [ "collection", "active" ]

class ListViewSet(viewsets.ModelViewSet):
    queryset = List.objects.all()
    serializer_class = ListSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = [ "reporter", "active" ]

class RecordViewSet(viewsets.ModelViewSet):
    queryset = Record.objects.all()
    serializer_class = RecordSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["active", "policy", "reporter", "list", "value"]
