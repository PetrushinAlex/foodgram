from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from tools import constants as cnst


User = get_user_model()


class Tag(models.Model):
    '''
    Модель для тэгов.
    Описаны поля:
    name - название тэга (str);
    color - цветовой код (HEX) (str);
    slug - название слага (str).
    В Meta классе по умолчанию сортировка по id.
    '''

    name = models.CharField(
        max_length=cnst.MAX_LENGHT_NAME,
        db_index=True,
        verbose_name='Тэг',
    )
    color = models.CharField(
        max_length=cnst.MAX_LENGHT_SMALL,
        verbose_name='Цвет',
    )
    slug = models.SlugField(
        max_length=cnst.MAX_LENGHT_NAME,
        verbose_name='Слаг',
        unique=True,
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
    Описаны поля:
    name - название ингредиента (str);
    measurement_unit - единица измерения (str).
    На уровне базы данных по умолчанию сортировка по названию.
    Также определена уникальная комбинация названия ингредиента
    и единицы его измерения.
    '''
    name = models.CharField(
        max_length=cnst.MAX_LENGHT_NAME,
        db_index=True,
        verbose_name='Ингредиент',
    )
    measurement_unit = models.CharField(
        max_length=cnst.MAX_LENGHT_NAME,
        verbose_name='Единица измерения',
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(
                fields=[
                    'name', 
                    'measurement_unit',
                ],
                name='uniqe_name_unit',
            )
        ]

    def __str__(self):
        return self.name


class Recipe(models.Model):
    '''
    Модель для рецептов.
    Описаны поля:
    name - название рецепта (str);
    text - описание рецепта (str);
    author - автор рецепта, это поле связано 
             с актуальной моделью пользователя;
    image - картинка для рецепта (img);
    tags - тэги к рецепту (many-to-many с моделью Tag);
    ingredients - ингредиенты к рецепту (many-to-many 
                  с моделью Ingredient);
    pub_date - автоматически добавляющаяся дата публикации;
    cooking_time - время приготовления с указанием границ (int).
    На уровне базы данных по умолчанию сортировка по названию.
    '''

    name = models.CharField(
        max_length=cnst.MAX_LENGHT_NAME,
        db_index=True,
        verbose_name='Рецепт',
    )
    text = models.TextField(
        verbose_name='Описание рецепта',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Пользователь',
    )
    image = models.ImageField(
        verbose_name='Ссылка для картинки рецепта на сайте',
        blank=True,
        null=True,
        upload_to='recipes/',
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
        through='RecipeIngredient',
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления (мин)',
        validators=[
            MinValueValidator(cnst.COOKING_TIME_MIN),
        ],
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class RecipeTag(models.Model):
    '''
    Модель для тэга рецепта, создающая
    промежуточную таблице (many-to-many связь).
    '''

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_tags',
        verbose_name='Рецепт',
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name='recipe_tags',
        verbose_name='Тэг',
    )

    class Meta:
        verbose_name = 'Тэг рецепта'
        verbose_name_plural = 'Тэги рецепта'
    
    def __str__(self):
        return self.tag.name


class RecipeIngredient(models.Model):
    '''
    Модель для ингредиентов в рецептах, создающая
    промежуточную таблице (many-to-many связь).
    '''

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name='Рецепт',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name='Ингредиент',
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество ингредиента',
        validators=[
            MinValueValidator(cnst.AMOUNT_RECIPE_INGREDIENT_MIN),
            MaxValueValidator(cnst.AMOUNT_RECIPE_INGREDIENT_MAX),
        ],
    )

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'
        ordering = ['id']

    def __str__(self):
        return f'{self.ingredient.name} ({self.amount}) для рецепта {self.recipe.name}'


class ShoppingCart(models.Model):
    '''
    Модель для корзины рецептов конкретного юзера, создающая 
    промежуточную таблицу между соответствующими моделями (many-to-many связь).
    '''

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Рецепт',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Пользователь',
    )

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'


class Favorite(models.Model):
    '''
    Модель для любимых рецептов конкретного юзера, создающая 
    промежуточную таблицу между соответствующими моделями (many-to-many связь).
    '''
    
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite',
        verbose_name='Рецепт',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite',
        verbose_name='Пользователь',
    )

    class Meta:
        verbose_name = 'Избранное'
