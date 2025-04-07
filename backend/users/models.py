from django.contrib.auth.models import AbstractUser
from django.db import models

from tools import constants as cnst


class CustomUser(AbstractUser):
    '''
    Модель пользователя на основе импортируемой абстрактной модели.
    '''

    username = models.CharField(
        max_length=cnst.MAX_LENGHT_NAME,
        verbose_name='Название аккаунта',
        unique=True,
        db_index=True,
    )
    email = models.EmailField(
        max_length=cnst.MAX_LENGHT_NAME,
        verbose_name='Электронная почта',
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


class Sub(models.Model):
    '''
    Модель для подписчиков, реализованная через связь many-to-many
    между моделями пользователей.
    '''

    user = models.ForeignKey(
        AbstractUser,
        on_delete=models.CASCADE,
        related_name='subs',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        AbstractUser,
        on_delete=models.CASCADE,
        related_name='subs',
        verbose_name='Автор',
    )

    class Meta:
        verbose_name = 'Подписчик'
        verbose_name_plural = 'Подписчики'
        ordering = ('-id',)
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'author',),
                name='unique_sub',
            )
        ]

        def __str__(self):
            return f'Пользователь {self.user.username} подписан на {self.author.username}'
