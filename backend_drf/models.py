from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from phonenumber_field.modelfields import PhoneNumberField

User = settings.AUTH_USER_MODEL


class Account(AbstractUser):
    # TODO: Изменить на настоящие должности по их грейдам
    CHOICES_ROLE = [
        ("JR", "Junior"),
        ("ME", "Middle"),
        ("SR", "Senior"),
        ("TL", "Team Leader"),
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

    title = models.CharField(max_length=256)
    authorID = models.ForeignKey('Account', on_delete=models.PROTECT)
    creation_date = models.DateTimeField(auto_now=True)
    material_link = models.URLField()
    fileID = models.ForeignKey('File', on_delete=models.PROTECT)
    article = models.TextField()
    state = models.CharField(max_length=15, choices=STATE_ARTICLE)
    formula_ids = models.ManyToManyField('Formula')

    # TODO: в дальнейшем нужно распарсить данные номера символов и ролей,
    #  для получения массива и нужной вложенности в JSON формате
    beginning_symbols = models.TextField()
    positions_list = models.CharField(max_length=256)

    versionID = models.ForeignKey('VersionsDocuments', on_delete=models.PROTECT)
    folderID = models.ForeignKey('Folder', on_delete=models.PROTECT)


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

class VersionsDocuments(models.Model):
    # TODO: в дальнейшем нужно распарсить данные на IDs статей,
    #  чтобы быстро найти связанные статьи в список
    # TODO: при редактировании не забывать добавлять новый ID статьи
    articles_ids = models.TextField()

