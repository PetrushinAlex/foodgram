from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField
from rest_framework.fields import SerializerMethodField

from food.models import (
    Recipe,
    Tag,
    Ingredient,
    ShoppingCart,
    RecipeIngredient,
    Favorite
)
from users.models import Sub

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Расширенный сериализатор пользователей.
    Добавляет информацию о подписках и аватаре.
    """

    is_subscribed = SerializerMethodField()
    avatar = Base64ImageField(
        required=False,
        allow_null=True,
    )

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_subscribed",
            "avatar",
        )
        read_only_fields = ("id", "is_subscribed")

    def get_is_subscribed(self, obj):
        """
        Определяет, подписан ли текущий пользователь на этого автора.
        """

        request = self.context.get("request")
        return (
                request
                and request.user.is_authenticated
                and request.user.subscriptions.filter(author=obj).exists()
        )


class SubscribeSerializer(UserSerializer):
    """Сериализатор для отображения подписок пользователя."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.ReadOnlyField(source="recipes.count")

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ("recipes", "recipes_count")
        read_only_fields = fields

    def get_recipes(self, obj):
        """Возвращает ограниченное количество рецептов пользователя."""
        request = self.context.get("request")
        recipes = obj.recipes.all()

        try:
            limit = int(request.GET.get("recipes_limit"))
            recipes = recipes[:limit]
        except (ValueError, TypeError):
            pass

        return RecipeSimpleSerializer(
            recipes, many=True, context=self.context
        ).data

    def validate(self, data):
        """Валидация при создании подписки"""
        user = self.context['request'].user
        author = self.context['view'].get_object()

        if user == author:
            raise serializers.ValidationError(
                {'subscribed_to': 'Нельзя подписаться на самого себя'}
            )

        if Sub.objects.filter(
                user=user,
                author=author
        ).exists():
            raise serializers.ValidationError(
                {'subscribed_to': 'Вы уже подписаны на этого пользователя'}
            )

        return data


class FavoriteShoppingCartSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())

    class Meta:
        fields = ('user', 'recipe')


class FavoriteSerializer(FavoriteShoppingCartSerializer):
    """Серик для избранного"""

    class Meta(FavoriteShoppingCartSerializer.Meta):
        model = Favorite

    def validate(self, data):
        """есть ли уже в избранном"""
        user = data['user']
        recipe = data['recipe']

        if Favorite.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError(
                f"Рецепт '{recipe.name}' уже в избранном"
            )
        return data


class ShoppingCartSerializer(FavoriteShoppingCartSerializer):
    """для добалвения."""

    class Meta(FavoriteShoppingCartSerializer.Meta):
        model = ShoppingCart
        extra_kwargs = {
            'recipe': {'write_only': True},
            'user': {'write_only': True}
        }

    def validate(self, data):
        """не добавлен ли"""
        user = data['user']
        recipe = data['recipe']

        if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError(
                f"Рецепт '{recipe.name}' уже в корзине покупок"
            )
        return data

    def to_representation(self, instance):
        """краткое представление"""
        return RecipeSimpleSerializer(
            instance.recipe,
            context=self.context
        ).data


class TagSerializer(serializers.ModelSerializer):
    """
    Преобразует данные о кулинарных тегах.
    """

    class Meta:
        model = Tag
        fields = (
            "id",
            "name",
            "slug",
        )


class IngredientSerializer(serializers.ModelSerializer):
    """
    Обрабатывает информацию об ингредиентах.
    Включает единицы измерения для каждого ингредиента.
    """

    class Meta:
        model = Ingredient
        fields = (
            "id",
            "name",
            "measurement_unit",
        )


class RecipeIngredientReadSerializer(serializers.ModelSerializer):
    """
    Сериализатор для чтения ингредиентов рецепта.
    Возвращает id, имя, ед. изм. и количество.
    """

    id = serializers.PrimaryKeyRelatedField(read_only=True, source="ingredient")
    name = serializers.CharField(source="ingredient.name", read_only=True)
    measurement_unit = serializers.CharField(
        source="ingredient.measurement_unit", read_only=True
    )

    class Meta:
        model = RecipeIngredient
        fields = ("id", "name", "measurement_unit", "amount")


class RecipeIngredientWriteSerializer(serializers.Serializer):
    """
    Сериализатор для записи ингредиентов рецепта.
    Здесь id — просто PrimaryKeyRelatedField без source,
    чтобы на входе был просто id (pk),
    а не объект Ingredient.
    """

    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(validators=[MinValueValidator(1)])

    def to_internal_value(self, data):
        """
        Переопределяем, чтобы id вернулся как число, а не объект.
        """
        validated_data = super().to_internal_value(data)
        validated_data["id"] = validated_data["id"].pk
        return validated_data


class RecipeSimpleSerializer(serializers.ModelSerializer):
    """
    Сокращенная версия данных о рецепте.
    Используется для вложенных представлений.
    """

    class Meta:
        model = Recipe
        fields = (
            "id",
            "name",
            "cooking_time",
            "image",
        )
        read_only_fields = (
            "id",
            "name",
            "cooking_time",
            "image",
        )


class RecipeReadSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = RecipeIngredientReadSerializer(
        many=True, source="recipe_ingredients", read_only=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = [
            "id",
            "tags",
            "author",
            "ingredients",
            "name",
            "image",
            "text",
            "cooking_time",
            "is_favorited",
            "is_in_shopping_cart",
        ]

    def get_is_favorited(self, obj):
        request = self.context.get("request")
        return (
                request
                and request.user.is_authenticated
                and obj.favorite.filter(user=request.user).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get("request")
        return (
                request
                and request.user.is_authenticated
                and obj.shopping_cart.filter(user=request.user).exists()
        )


class RecipeWriteSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        write_only=True,
    )

    ingredients = RecipeIngredientWriteSerializer(
        many=True,
        source="recipe_ingredients",
    )
    image = Base64ImageField(required=True)
    cooking_time = serializers.IntegerField(
        validators=[
            MinValueValidator(
                1, message="Время приготовления не может быть меньше 1 минуты"
            ),
            MaxValueValidator(
                9999, message="Время приготовления не может превышать 9999 минут"
            ),
        ],
    )

    class Meta:
        model = Recipe
        fields = [
            "id",
            "tags",
            "author",
            "ingredients",
            "name",
            "image",
            "text",
            "cooking_time",
        ]

    def validate(self, data):
        """
        Комплексная проверка данных рецепта.
        Контролирует теги, ингредиенты, время приготовления и изображение.
        """

        t = data.get("tags", [])
        ingredients = data.get("recipe_ingredients", [])
        image = data.get("image")
        cooking_time = data.get("cooking_time")

        if self.context["request"].method == "POST" and (image is None or image == ""):
            raise serializers.ValidationError({"image": "Изображение не заполненно"})

        if not t:
            raise serializers.ValidationError({"tags": "Поле Тег  не заполненно"})

        t_ids = [tag.id for tag in t]
        if len(t_ids) != len(set(t_ids)):
            raise serializers.ValidationError({"tags": "Дублирование тегов!."})

        if not ingredients:
            raise serializers.ValidationError(
                {"ingredient": "Поле Ингридиент  не заполненно"}
            )
        for ingredient in ingredients:
            amount = ingredient.get("amount")
            if amount is None:
                raise serializers.ValidationError({"amount": "Нет количества"})
            if not (1 <= amount <= 9999):
                raise serializers.ValidationError(
                    {"amount": f"Кол-во должно быть между {1} и {9999}."}
                )

        if len(ingredients) != len({i["id"] for i in ingredients}):
            raise serializers.ValidationError(
                {"ingredients": "Ингредиенты не должны повторяться."}
            )
        if cooking_time is None:
            raise serializers.ValidationError(
                {"cooking_time": "Время приготовления обязательно."}
            )
        if not (1 <= cooking_time <= 9999):
            raise serializers.ValidationError(
                {"cooking_time": f"Время должно быть {1} - {9999} мин."}
            )
        if image is None or image == "":
            raise serializers.ValidationError({"image": "Изображение  не заполненно"})

        return data

    def create(self, validated_data):
        """
        Создает новый рецепт с указанными тегами и ингредиентами.
        """

        i_data = validated_data.pop("recipe_ingredients", [])
        t_data = validated_data.pop("tags", [])

        validated_data.pop("author", None)

        author = self.context["request"].user

        recipe = Recipe.objects.create(author=author, **validated_data)

        recipe.tags.set(t_data)
        self.ing_up_and_cr(recipe, i_data)

        return recipe

    def ing_up_and_cr(self, recipe, ingredients_data):
        """
        Внутренний метод для обработки ингредиентов.
        Создает связи между рецептом и ингредиентами.
        """

        recipe_ingredients = [
            RecipeIngredient(
                recipe=recipe,
                ingredient_id=ingredient_data["id"],
                amount=ingredient_data["amount"],
            )
            for ingredient_data in ingredients_data
        ]
        RecipeIngredient.objects.bulk_create(recipe_ingredients)
        return recipe_ingredients

    def update(self, instance, validated_data):
        """
        Обновляет существующий рецепт.
        Полностью заменяет теги и ингредиенты.
        """
        image = validated_data.get("image")
        if image == "":
            raise serializers.ValidationError(
                {"image": "Изображение не может быть пустым."}
            )

        if "image" not in validated_data:
            validated_data["image"] = instance.image

        i_data = validated_data.pop("recipe_ingredients", [])
        t_data = validated_data.pop("tags", [])

        instance = super().update(instance, validated_data)

        instance.tags.set(t_data)

        instance.recipe_ingredients.all().delete()
        self.ing_up_and_cr(instance, i_data)

        return instance

    def to_representation(self, instance):
        return RecipeReadSerializer(instance, context=self.context).data


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=True)

    class Meta:
        model = User
        fields = ["avatar"]
