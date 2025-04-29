from django.contrib.auth.models import AbstractUser
from django.db import models

from tools import constants as cnst


class CustomUser(AbstractUser):
    '''
    Модель пользователя на основе импортируемой абстрактной модели.
    Переопределены поля юзернейма, электронной почты, имени и фамилии.
    На уровне базы данных задана сортировка по id.
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
    Описаны поля:
    author - автор рецепта, на кого подписан другой пользователь
             (связь через модель пользователя).
    user - подписчик на автора (аналогично с автором через модель юзера).
    На уровне базы данных прописана уникальность связи 
    полей автор-подписчик.
    '''

    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='subscription',
        verbose_name='Автор',
    )
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='Подписчик',
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
