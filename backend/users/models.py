from django.contrib.auth.models import AbstractUser
from django.db import models

from food import constants


class ExtendedUser(AbstractUser):
    """
    Модель пользователя на основе импортируемой абстрактной модели.
    Переопределены поля юзернейма, электронной почты, имени и фамилии.
    На уровне базы данных задана сортировка по id.
    """

    email = models.EmailField(
        verbose_name='Электронная почта',
        unique=True,
    )
    first_name = models.CharField(
        max_length=constants.MAX_LENGHT_NAME,
        verbose_name='Имя',
    )
    last_name = models.CharField(
        max_length=constants.MAX_LENGHT_NAME,
        verbose_name='Фамилия',
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        default='avatars/default_avatar.png',
        null=True,
    )

    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'password']
    USERNAME_FIELD = 'email'

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'Пользователь {self.username} ({self.email})'


class Sub(models.Model):
    """
    Модель для подписчиков, реализованная через связь many-to-many
    между моделями пользователей.
    Описаны поля:
    author - автор рецепта, на кого подписан другой пользователь
             (связь через модель пользователя).
    user - подписчик на автора (аналогично с автором через модель юзера).
    На уровне базы данных прописана уникальность связи
    полей автор-подписчик.
    """

    user = models.ForeignKey(
        ExtendedUser,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='кто подписался',
    )
    author = models.ForeignKey(
        ExtendedUser,
        on_delete=models.CASCADE,
        related_name='users_subscribers',
        verbose_name='на кого подписались',
    )

    class Meta:
        verbose_name = 'Подписчик'
        verbose_name_plural = 'Подписчики'
        constraints = [
            models.UniqueConstraint(
                fields=(
                    'user',
                    'author',
                ),
                name='unique_sub',
            )
        ]

        def __str__(self):
            return (
                f'Пользователь {self.user.username} '
                f'подписан на {self.author.username}'
            )
