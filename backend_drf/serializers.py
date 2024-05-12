from rest_framework import serializers, fields
from .models import *

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

    class Meta:
        model = Article
        fields = ('title', 'material_link', 'fileID', 'article',
                  'formula_ids', 'folderID', 'access')


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

        # Add formula_ids if provided
        if 'formula_ids' in validated_data:
            formula_ids = validated_data['formula_ids']
            for formula_id in formula_ids:
                formula = Formula.objects.get(id=formula_id)
                article.formula_ids.add(formula)

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