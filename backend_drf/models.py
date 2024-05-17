from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from phonenumber_field.modelfields import PhoneNumberField
from multiselectfield import MultiSelectField
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.fields import JSONField

User = settings.AUTH_USER_MODEL


class Account(AbstractUser):
    CHOICES_ROLE = [
        ("AD", "Administrator"),
        ("DI", "Director"),
        ("AC", "Accountant"),
        ("AR", "Architect"),
        ("CE", "Civil-Engineer"),
        ("LA", "Lawyer"),
        ("PL", "Planner"),
    ]

    REQUIRED_FIELDS = ["email", "role"]

    role = models.CharField(max_length=15, choices=CHOICES_ROLE)
    phone_number = PhoneNumberField(region='RU')
    patronymic = models.CharField(max_length=128, blank=True, null=True)
    work_pos = models.CharField(max_length=128)


class Article(models.Model):
    STATE_ARTICLE = [
        ("AC", "Active"),
        ("LA", "Last"),
        ("AR", "Archive"),
    ]
    CHOICES_ROLE = [
        ("AD", "Administrator"),
        ("DI", "Director"),
        ("AC", "Accountant"),
        ("AR", "Architect"),
        ("CE", "Civil-Engineer"),
        ("LA", "Lawyer"),
        ("PL", "Planner"),
    ]

    title = models.CharField(max_length=256)
    authorID = models.ForeignKey('Account', on_delete=models.PROTECT)
    creation_date = models.DateTimeField(auto_now_add=True)
    material_link = models.URLField(null=True)
    fileID = models.ForeignKey('File', on_delete=models.PROTECT, null=True)
    article = models.TextField()
    state = models.CharField(max_length=15, choices=STATE_ARTICLE)
    formula_ids = models.ManyToManyField('Formula', null=True, blank=True)

    versionID = models.ForeignKey('VersionsDocuments', on_delete=models.PROTECT)
    folderID = models.ForeignKey('Folder', on_delete=models.PROTECT)

    access = MultiSelectField(choices=CHOICES_ROLE, max_length=256)

    changed = models.TextField(null=True, blank=True)


class Formula(models.Model):
    formula = models.TextField()
    variables = models.JSONField(default=dict)


class Comment(models.Model):
    content = models.CharField(max_length=1000)
    userID = models.ForeignKey('Account', on_delete=models.PROTECT)
    articleID = models.ForeignKey('Article', on_delete=models.PROTECT)


class File(models.Model):
    articleID = models.ForeignKey('Article', on_delete=models.PROTECT)
    file = models.FileField()


class FunctionalModels(models.Model):
    articleID = models.ForeignKey('Article', on_delete=models.PROTECT)
    model = models.TextField()


class Folder(models.Model):
    title = models.CharField(max_length=256)
    articles_ids = ArrayField(models.IntegerField(), blank=True, null=True)

class VersionsDocuments(models.Model):
    # TODO: в дальнейшем нужно распарсить данные на IDs статей,
    #  чтобы быстро найти связанные статьи в список
    articles_ids = ArrayField(models.IntegerField(), blank=True, null=True)

