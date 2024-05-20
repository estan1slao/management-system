from rest_framework import serializers, fields
from .models import *
from .decorators import access_control
from django.utils import timezone

CHOICES_ROLE = [
    ("AD", "Administrator"),
    ("DI", "Director"),
    ("AC", "Accountant"),
    ("AR", "Architect"),
    ("CE", "Civil-Engineer"),
    ("LA", "Lawyer"),
    ("PL", "Planner"),
]


class ArticleSerializer(serializers.ModelSerializer):
    access = serializers.ListField(
        child=serializers.ChoiceField(choices=CHOICES_ROLE),
        required=False
    )
    author = serializers.SerializerMethodField()
    changed_by_author = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = ('id', 'title', 'creation_date', 'material_link', 'fileID', 'article', 'author', 'changed_by_author',
                  'formula_ids', 'folderID', 'access', 'changed', 'versionID')
        extra_kwargs = {
            'title': {'required': False},
            'article': {'required': False},
            'folderID': {'required': False},
        }

    def get_author(self, obj):
        account = obj.authorID
        return f"{account.last_name} {account.first_name}"

    def get_changed_by_author(self, obj):
        account = obj.changed_by_author
        if account is None:
            account = obj.authorID
        return f"{account.last_name} {account.first_name}"

    def create(self, validated_data):
        user = self.context['request'].user

        vers = VersionsDocuments.objects.create()

        article = Article.objects.create(
            title=validated_data['title'],
            authorID=user,
            material_link=validated_data.get('material_link'),
            fileID=validated_data.get('fileID'),
            article=validated_data['article'],
            state='AC',
            versionID=vers,
            folderID=validated_data['folderID'],
            access=validated_data['access'],
        )

        if 'formula_ids' in validated_data:
            formula_ids = validated_data['formula_ids']
            for formula_id in formula_ids:
                article.formula_ids.add(formula_id.id)

        if vers.articles_ids is None:
            vers.articles_ids = []

        vers.articles_ids.append(article.id)
        vers.save()

        if validated_data['folderID'].articles_ids is None:
            validated_data['folderID'].articles_ids = []

        validated_data['folderID'].articles_ids.append(article.id)
        validated_data['folderID'].save()

        article.save()

        return article

    def update(self, instance, validated_data):
        user = self.context['request'].user

        old_creation_date = instance.creation_date
        new_folder = validated_data.get('folderID')
        old_folder = instance.folderID

        old_article = Article.objects.create(
            title=instance.title,
            authorID=instance.authorID,
            material_link=instance.material_link,
            fileID=instance.fileID,
            article=instance.article,
            state='LA',
            versionID=instance.versionID,
            folderID=instance.folderID,
            access=instance.access,
            changed=instance.changed
        )
        old_article.creation_date = old_creation_date
        old_article.save()

        instance.title = validated_data.get('title', instance.title)
        instance.material_link = validated_data.get('material_link', instance.material_link)
        instance.fileID = validated_data.get('fileID', instance.fileID)
        instance.article = validated_data.get('article', instance.article)
        instance.folderID = validated_data.get('folderID', instance.folderID)
        instance.access = validated_data.get('access', instance.access)
        instance.changed = validated_data.get('changed', None)
        instance.changed_by_author = user

        instance.creation_date = timezone.now()

        if 'formula_ids' in validated_data:
            instance.formula_ids.clear()
            formula_ids = validated_data['formula_ids']
            for formula_id in formula_ids:
                instance.formula_ids.add(formula_id.id)

        instance.save()

        instance.versionID.articles_ids.append(old_article.id)
        instance.versionID.save()

        if new_folder != old_folder and new_folder is not None:
            if old_folder.articles_ids:
                old_folder.articles_ids.remove(instance.id)
                old_folder.save()

            if new_folder.articles_ids is None:
                new_folder.articles_ids = []
            new_folder.articles_ids.append(instance.id)
            new_folder.save()

        return instance


class FolderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Folder
        fields = ('id', 'title')


class FullFolderListSerializer(serializers.ModelSerializer):
    articles = serializers.SerializerMethodField()

    class Meta:
        model = Folder
        fields = ('id', 'title', 'articles')

    def get_articles(self, obj):
        article_ids = obj.articles_ids if obj.articles_ids else []
        articles = Article.objects.filter(id__in=article_ids)
        return ShortArticleListSerializer(articles, many=True).data


class FormulaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Formula
        fields = '__all__'


class ArticleListSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = ['id', 'changed', 'title', 'author', 'creation_date']

    def get_author(self, obj):
        account = obj.authorID
        return f"{account.last_name} {account.first_name}"


class ShortArticleListSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    class Meta:
        model = Article
        fields = ['id', 'title', 'author', 'creation_date']

    def get_author(self, obj):
        account = obj.authorID
        return f"{account.last_name} {account.first_name}"




