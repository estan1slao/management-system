from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from phonenumber_field.modelfields import PhoneNumberField
from multiselectfield import MultiSelectField

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
    patronymic = models.CharField(max_length=128)
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
    creation_date = models.DateTimeField(auto_now=True)
    material_link = models.URLField(null=True)
    fileID = models.ForeignKey('File', on_delete=models.PROTECT, null=True)
    article = models.TextField()
    state = models.CharField(max_length=15, choices=STATE_ARTICLE)
    formula_ids = models.ManyToManyField('Formula', null=True, blank=True)

    versionID = models.ForeignKey('VersionsDocuments', on_delete=models.PROTECT)
    folderID = models.ForeignKey('Folder', on_delete=models.PROTECT)

    access = MultiSelectField(choices=CHOICES_ROLE, max_length=256)


class Formula(models.Model):
    formula = models.TextField()


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
    # TODO: нужно ли добавить аналогичный articles_ids, как в VersionsDocuments?

class VersionsDocuments(models.Model):
    content = models.TextField(null=True)
    # TODO: в дальнейшем нужно распарсить данные на IDs статей,
    #  чтобы быстро найти связанные статьи в список
    # TODO: при редактировании не забывать добавлять новый ID статьи
    articles_ids = models.TextField(null=True)

