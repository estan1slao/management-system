from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
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
from django.http import HttpResponseForbidden
from django.http import JsonResponse


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
        article.state = 'AR'

        folder = get_object_or_404(Folder, id=article.folderID.id)
        if article.id in folder.articles_ids:
            folder.articles_ids.remove(article.id)
            folder.save()

        article.folderID = None

        article.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ArchiveArticlesView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        articles = Article.objects.filter(state='AR')
        accessible_articles = [article for article in articles]
        serializer = ShortArticleListSerializer(accessible_articles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class VersionDocumentsArticlesView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, version_id, *args, **kwargs):
        version_document = get_object_or_404(VersionsDocuments, id=version_id)
        articles_ids = version_document.articles_ids
        articles = Article.objects.filter(id__in=articles_ids)
        serializer = ArticleListSerializer(articles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class FolderView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        try:
            if 'id_folder' in kwargs:
                folder = Folder.objects.get(id=kwargs['id_folder'])
                serializer = FullFolderListSerializer(folder)
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

        if id_new_folder is not None:
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
        title = request.data.get('title')
        content = request.data.get('formula')
        variables = request.data.get('variables', {})
        formula = Formula.objects.create(formula=content, variables=variables, title=title)
        serializer = FormulaSerializer(formula)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request, id_formula, *args, **kwargs):
        try:
            formula = Formula.objects.get(id=id_formula)

            content = request.data.get('formula', None)
            if content is not None:
                formula.formula = content

            if 'variables' in request.data:
                variables = request.data.get('variables', {})
                formula.variables = variables

            title = request.data.get('title', None)
            if title is not None:
                formula.title = title

            formula.save()
            serializer = FormulaSerializer(formula)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({'error': 'Formula not found'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, id_formula, *args, **kwargs):
        try:
            formula = Formula.objects.get(id=id_formula)
            formula.delete()
            return Response({'message': 'Formula deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except ObjectDoesNotExist:
            return Response({'error': 'Formula not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getProfile(request):
    user = request.user
    serializer = ProfileSerializer(user, many=False)
    return Response(serializer.data)


@api_view(['GET'])
def search_articles(request, title):
    # Переводим название документа в нижний регистр
    query = title.lower()

    # Поиск статей по названию с учетом регистра и состоянию
    articles = Article.objects.filter(title__icontains=query, state="AC")

    # Сериализация результатов
    serializer = ShortArticleListSerializer(articles, many=True)
    return Response(serializer.data)


class ProfileAPIView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        profiles = Account.objects.all()
        serializer = ProfileSerializer(profiles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RestoreArticleAPIView(APIView):
    @access_control
    def post(self, request, pk):
        new_folder_id = request.data.get('folderID')
        new_folder = get_object_or_404(Folder, id=new_folder_id)

        article = get_object_or_404(Article, pk=pk)
        article.folderID = new_folder
        article.state = 'AC'
        article.save()

        if pk not in new_folder.articles_ids:
            new_folder.articles_ids.append(pk)
            new_folder.save()

        return Response(status=status.HTTP_200_OK)


class CommentListCreateView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, article_id):
        comments = Comment.objects.filter(articleID=article_id)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request, article_id):
        article = get_object_or_404(Article, id=article_id)
        user = request.user

        if user.role not in article.access:
            return Response({"error": "You do not have permission to comment on this article."},
                            status=status.HTTP_403_FORBIDDEN)

        data = request.data.copy()
        data['articleID'] = article_id
        data['userID'] = user.id
        serializer = CommentCreateSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentDeleteView(APIView):
    permission_classes = (IsAuthenticated,)

    def delete(self, request, comment_id):
        comment = get_object_or_404(Comment, id=comment_id)
        user = request.user

        if comment.userID != user:
            return Response({"error": "You do not have permission to delete this comment."},
                            status=status.HTTP_403_FORBIDDEN)

        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)