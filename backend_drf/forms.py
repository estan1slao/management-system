from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Account, User


class AccountCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Account
        fields = '__all__'
