from neo4django.db import models
from neo4django.graph_auth.models import User
from rest_framework import viewsets

from api.serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
