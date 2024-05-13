from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.generics import get_object_or_404
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
from rest_framework.viewsets import ModelViewSet
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist



class ArticleViewSet(ViewSet):
    permission_classes = (IsAuthenticated,)

    def create(self, request):
        serializer = ArticleSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @access_control
    def update(self, request, pk=None):
        article = get_object_or_404(Article, pk=pk)
        serializer = ArticleSerializer(article, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @access_control
    def retrieve(self, request, pk=None):
        article = get_object_or_404(Article, pk=pk)
        serializer = ArticleSerializer(article)
        return Response(serializer.data)

    @access_control
    def delete(self, request, pk=None):
        article = get_object_or_404(Article, pk=pk)
        article.state = 'AR'  # Изменяем состояние статьи на 'AR'
        article.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FolderView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        try:
            if 'id_folder' in kwargs:
                folder = Folder.objects.get(id=kwargs['id_folder'])
                serializer = FolderSerializer(folder)
            else:
                # Получаем список всех папок
                folders = Folder.objects.all()
                serializer = FolderSerializer(folders, many=True)
            return Response(serializer.data)
        except ObjectDoesNotExist:
            return Response({'error': 'Folder not found'}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, *args, **kwargs):
        # Создаем папку
        title = request.data.get('title')
        folder = Folder.objects.create(title=title)
        serializer = FolderSerializer(folder)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request, id_folder, *args, **kwargs):
        # Редактирование названия папки
        folder = Folder.objects.get(id=id_folder)
        title = request.data.get('title')
        folder.title = title
        folder.save()
        return Response({'message': 'Folder title updated successfully'}, status=status.HTTP_200_OK)

    def delete(self, request, id_folder, *args, **kwargs):
        # Удаление папки
        folder = Folder.objects.get(id=id_folder)
        id_new_folder = request.data.get('new_id_folder')

        new_folder = Folder.objects.get(id=id_new_folder)
        if new_folder is not None:
            for article in folder.articles_ids:
                if new_folder.articles_ids is None:
                    new_folder.articles_ids = []
                new_folder.articles_ids.append(article)

                obj_article = Article.objects.get(id=article)
                obj_article.folderID = new_folder
                obj_article.save()

            new_folder.save()
            for article in Article.objects.filter(folderID=folder):
                article.folderID = new_folder
                article.save()
            folder.delete()
            return Response({'message': 'Folder deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        else:
            if folder.articles_ids is None:
                folder.articles_ids = []
            if len(folder.articles_ids) > 0:
                return Response({'message': 'There are articles in the folder. Specify in the "new_id_folder" parameter the ID of the new folder where to move incoming articles'}, status=status.HTTP_400_BAD_REQUEST)
            folder.delete()
            return Response({'message': 'Folder deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


class FormulaView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        try:
            if 'id_formula' in kwargs:
                formula = Formula.objects.get(id=kwargs['id_formula'])
                serializer = FormulaSerializer(formula)
            else:
                formuls = Formula.objects.all()
                serializer = FormulaSerializer(formuls, many=True)
            return Response(serializer.data)
        except ObjectDoesNotExist:
            return Response({'error': 'Formula not found'}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, *args, **kwargs):
        content = request.data.get('formula')
        formula = Formula.objects.create(formula=content)
        serializer = FormulaSerializer(formula)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request, id_formula, *args, **kwargs):
        formula = Formula.objects.get(id=id_formula)
        content = request.data.get('formula')
        formula.formula = content
        formula.save()
        return Response({'message': 'Formula updated successfully'}, status=status.HTTP_200_OK)

    def delete(self, request, id_formula, *args, **kwargs):
        formula = Formula.objects.get(id=id_formula)
        try:
            formula.delete()
            return Response({'message': 'Formula deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except:
            return Response({'message': 'Before deleting a formula, you need to delete the formula from the articles!'}, status=status.HTTP_400_BAD_REQUEST)