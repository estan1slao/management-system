from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from .models import Account
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import viewsets, mixins, status, generics
from rest_framework.viewsets import GenericViewSet
from .models import *
from .serializers import *
from rest_framework.permissions import IsAdminUser, AllowAny, IsAuthenticated


class CreateArticleView(mixins.CreateModelMixin,
                        GenericViewSet):
    queryset = Article.objects.all()
    permission_classes = (IsAuthenticated, )
    serializer_class = ArticleSerializer
