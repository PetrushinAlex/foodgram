from django.contrib.auth import get_user_model
from django.db import models

from tools import constants as cnst


User = get_user_model()


class Tag(models.Model):
    '''
    Модель для тэгов
    '''

    name = models.CharField(
        max_length=cnst.MAX_LENGHT_NAME,
        db_index=True,
        verbose_name='Тэг',
    )
    color = models.CharField(
        max_length=10,
        verbose_name='слаг',
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        ordering = ['id']

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    '''
    Модель для ингредиентов.
    '''
    name = models.CharField(
        max_length=cnst.MAX_LENGHT_NAME,
        db_index=True,
        verbose_name='Ингредиент',
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['name']

    def __str__(self):
        return self.name


class Recipe(models.Model):
    '''
    Модель для рецептов.
    '''

    name = models.CharField(
        max_length=cnst.MAX_LENGHT_NAME,
        db_index=True,
        verbose_name='Рецепт',
    )
    text = models.TextField(
        verbose_name='Описание рецепта',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Пользователь',
    )
    image = models.ImageField(
        verbose_name='Картинка для рецепта',
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Тэги',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name='recipes',
        verbose_name='Ингредиенты',
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['name']
    
    def __str__(self):
        return self.name
