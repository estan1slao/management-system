from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Account
from .forms import AccountCreationForm


class CustomUserAdmin(UserAdmin):
    add_form = AccountCreationForm
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'role', 'phone_number', 'patronymic', 'work_pos', 'password1', 'password2')}
         ),
    )
    fieldsets = (
        (None, {'fields': ('username', 'email', 'role', 'phone_number', 'patronymic', 'work_pos')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    list_display = ('username', 'email', 'role', 'phone_number', 'patronymic', 'work_pos')
    readonly_fields = ('last_login', 'date_joined', 'is_staff', 'is_superuser')


admin.site.register(Account, CustomUserAdmin)