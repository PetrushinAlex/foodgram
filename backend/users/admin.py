from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from . import models


@admin.register(models.CustomUser)
class CustomUserAdmin(UserAdmin):
    '''
    Кастомный класс для регистрации модели пользователя в админке.
    '''
    list_display = (
        'id',
        'username',
        'email',
        'first_name',
        'last_name',
    )
    list_filter = (
        'username',
        'email',
    )
    search_fields = (
        'username',
        'email',
        'first_name',
        'last_name',
    )
