from django.contrib.auth import get_user_model
from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField
from rest_framework.fields import SerializerMethodField

from food.models import (
    Recipe,
    Tag,
    Ingredient,
    ShoppingCart,
    RecipeIngredient,
    Favorite,
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


class SubscribeSerializer(UserSerializer):

    """Сериализатор для отображения подписок пользователя."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.ReadOnlyField(source="recipes.count")

    class Meta:
        model = User
        fields = UserSerializer.Meta.fields + (
            "recipes",
            "recipes_count",
        )

    def get_is_subscribed(self, obj):
        return True

    def get_recipes(self, obj):
        """Возвращает ограниченное количество рецептов пользователя."""
        request = self.context.get("request")
        recipes = obj.recipes.all()

        try:
            limit = int(request.GET.get("recipes_limit", 0))
            recipes = recipes[:limit]
        except (ValueError, TypeError):
            pass

        return RecipeSimpleSerializer(
            recipes,
            many=True,
            context=self.context
        ).data


class SubscriptionCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания подписки."""

    class Meta:
        model = Sub
        fields = ("user", "author")

    def validate(self, data):
        """Валидация при создании подписки."""
        user = data["user"]
        author = data["author"]

        if user == author:
            raise serializers.ValidationError(
                {"subscribed_to": "Нельзя подписаться на себя"}
            )

        if Sub.objects.filter(user=user, author=author).exists():
            raise serializers.ValidationError(
                {"subscribed_to": "Вы уже подписаны"}
            )

        return data

    def to_representation(self, instance):
        """Возвращаем данные автора в AuthorWithRecipesSerializer."""
        author_serializer = AuthorWithRecipesSerializer(
            instance.author,
            context=self.context
        )
        return author_serializer.data


class FavoriteShoppingCartSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())

    class Meta:
        fields = ("user", "recipe")


class FavoriteSerializer(FavoriteShoppingCartSerializer):
    """Сериализатор для избранного."""

    class Meta(FavoriteShoppingCartSerializer.Meta):
        model = Favorite

    def validate(self, data):
        """Есть ли уже в избранном."""
        user = data["user"]
        recipe = data["recipe"]

        if Favorite.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError(
                f"Рецепт '{recipe.name}' уже в избранном."
            )
        return data


class RecipeShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class ShoppingCartSerializer(FavoriteShoppingCartSerializer):
    """Для добавления."""

    class Meta(FavoriteShoppingCartSerializer.Meta):
        model = ShoppingCart
        extra_kwargs = {
            "recipe": {"write_only": True}, "user": {"write_only": True}
        }

    def validate(self, data):
        """Не добавлен ли."""
        user = data["user"]
        recipe = data["recipe"]

        if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError(
                f"Рецепт '{recipe.name}' уже в корзине покупок"
            )
        return data

    def to_representation(self, instance):
        """Краткое представление."""
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

    id = serializers.PrimaryKeyRelatedField(
        read_only=True,
        source="ingredient"
    )
    name = serializers.CharField(source="ingredient.name", read_only=True)
    measurement_unit = serializers.CharField(
        source="ingredient.measurement_unit", read_only=True
    )

    class Meta:
        model = RecipeIngredient
        fields = ("id", "name", "measurement_unit", "amount")


class RecipeIngredientWriteSerializer(serializers.ModelSerializer):
    """
    Сериализатор для записи ингредиентов рецепта.
    Здесь id — просто PrimaryKeyRelatedField без source,
    чтобы на входе был просто id (pk),
    а не объект Ingredient.
    """

    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        model = RecipeIngredient
        fields = ("id", "amount")

    def to_internal_value(self, data):
        """
        Переопределяем, чтобы id вернулся как число, а не объект.
        """
        validated_data = super().to_internal_value(data)
        validated_data["id"] = validated_data["id"].pk
        return validated_data


class AuthorSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    avatar = serializers.ImageField(allow_null=True)

    class Meta:
        model = User
        fields = UserSerializer.Meta.fields

    def get_is_subscribed(self, obj):
        user = self.context.get("request").user
        if not user.is_authenticated:
            return False
        return Sub.objects.filter(user=user, author=obj).exists()


class AuthorWithRecipesSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = UserSerializer.Meta.fields + (
            "recipes",
            "recipes_count",
        )

    def get_is_subscribed(self, obj):
        user = self.context["request"].user
        return (
            user.is_authenticated and Sub.objects.filter(
                user=user,
                author=obj
            ).exists()
        )

    def get_recipes(self, obj):
        request = self.context.get("request")
        recipes = obj.recipes.all()

        try:
            limit = int(request.GET.get("recipes_limit", 0))
            if limit > 0:
                recipes = recipes[:limit]
        except (ValueError, TypeError):
            pass

        return RecipeShortSerializer(
            recipes,
            many=True,
            context=self.context
        ).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


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

        if not t:
            raise serializers.ValidationError(
                {"tags": "Поле Тег не заполненно"}
            )

        t_ids = [tag.id for tag in t]
        if len(t_ids) != len(set(t_ids)):
            raise serializers.ValidationError({"tags": "Дублирование тегов!"})

        if not ingredients:
            raise serializers.ValidationError(
                {"ingredient": "Поле Ингредиент не заполненно"}
            )

        if len(ingredients) != len({i["id"] for i in ingredients}):
            raise serializers.ValidationError(
                {"ingredients": "Ингредиенты не должны повторяться."}
            )

        return data

    def validate_image(self, value):
        """
        Проверяет, что изображение заполнено при создании нового рецепта.
        """

        if not value:
            raise serializers.ValidationError("Изображение не заполненно")

        return value

    def create(self, validated_data):
        """
        Создает новый рецепт с указанными тегами и ингредиентами.
        """

        i_data = validated_data.pop("recipe_ingredients", [])
        t_data = validated_data.pop("tags", [])

        validated_data["author"] = self.context["request"].user

        recipe = Recipe.objects.create(**validated_data)

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

    def update(self, instance, validated_data):
        """
        Обновляет существующий рецепт.
        Полностью заменяет теги и ингредиенты.
        """

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
