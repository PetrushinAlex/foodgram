from django.contrib.auth.models import AbstractUser
from django.db import models

from tools import constants as cnst


class CustomUser(AbstractUser):
    '''
    Модель пользователя на основе импортируемой абстрактной модели.
    '''
    email = models.EmailField(
        verbose_name='Электронная почта',
        max_length=cnst.MAX_LENGHT_NAME,
        unique=True,
    )
    first_name = models.CharField(
        max_length=cnst.MAX_LENGHT_NAME,
        verbose_name='Имя',
    )
    last_name = models.CharField(
        max_length=cnst.MAX_LENGHT_NAME,
        verbose_name='Фамилия',
    )

    class Meta:
        ordering = ['id']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username
