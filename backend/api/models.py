from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    '''
    Модель пользователя на основе импортируемой абстрактной модели.
    '''
    pass


class Recipe(models.Model):
    '''
    Модель для рецептов.
    '''
    pass


class Tag(models.Model):
    '''
    Модель для тэгов
    '''
    pass


class Ingredient(models.Model):
    '''
    Модель для ингредиентов.
    '''
    pass
