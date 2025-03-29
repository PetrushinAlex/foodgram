from django.db import models

from tools import constants as cnst


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
