from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly
)

from . import models, serializers as srls
from tools import paginators


User = get_user_model()


class CustomUserViewSet(UserViewSet):
    '''
    Кастомное представление для пользователей.
    '''

    queryset = User.objects.all()
    serializer_class = srls.CustomUserSerializer
    pagination_class = paginators.CustomPaginator
    permission_classes = (IsAuthenticatedOrReadOnly,)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated],
    )
    def subscribe(self, request, **kwargs):
        user = request.user
        author = get_object_or_404(
            User,
            id=self.kwargs.get('id'),
        )

        if request.method == 'POST':
            serializer = srls.SubSerializer(
                author,
                data=request.data,
                context={'request': request},
            )
            serializer.is_valid(raise_exception=True)
            models.Sub.objects.create(
                user=user,
                author=author,
            )
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
            )

        if request.method == "DELETE":
            subscription = get_object_or_404(
                models.Sub, 
                user=user, 
                author=author,
            )
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(
        detail=False,
        permission_classes=[IsAuthenticated],
    )
    def subscriptions(self, request):
        queryset = User.objects.filter(
            subscription__user=request.user,
        )
        pages = self.paginate_queryset(queryset)
        serializer = srls.SubSerializer(
            pages, 
            many=True, 
            context={"request": request},
        )
        return self.get_paginated_response(serializer.data)
