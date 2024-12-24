from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.parsers import JSONParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.pagination import StandardPagination
from api.serializers import (AvatarUpdateSerializer, CreateFollowSerializer,
                             FollowSerializer, StandartUserSerializer)

from .models import Follow, User


class StandartUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = StandartUserSerializer
    pagination_class = StandardPagination
    permission_classes = [AllowAny]

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated],)
    def me(self, request):
        """Метод для получения информации о текущем пользователе."""

        serializer = StandartUserSerializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['put'],
            permission_classes=[IsAuthenticated],
            parser_classes=[JSONParser],
            url_path='me/avatar')
    def avatar_put(self, request):
        """Метод для загрузки или обновления аватара пользователя."""
        user = request.user

        if 'avatar' not in request.data:
            return Response({"error": "Поле 'avatar' обязательно."},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = AvatarUpdateSerializer(user, data=request.data,
                                            partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @avatar_put.mapping.delete
    def avatar_delete(self, request):
        """Метод для удаления аватара пользователя."""
        user = request.user
        if user.avatar:
            user.avatar.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({"detail": "Аватар не найден."},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'],
            permission_classes=[IsAuthenticated],
            url_path='subscribe', url_name='subscribe')
    def create_subscription(self, request, **kwargs):
        author_id = self.kwargs.get('id')
        author = get_object_or_404(User, id=author_id)
        serializer = CreateFollowSerializer(data={'author': author.id},
                                            context={"request": request})
        serializer.is_valid(raise_exception=True)
        follow = serializer.save()
        return Response(FollowSerializer(
            follow, context={"request": request}).data,
            status=status.HTTP_201_CREATED)

    @create_subscription.mapping.delete
    def delete_subscription(self, request, **kwargs):
        user = request.user
        author_id = self.kwargs.get('id')
        author = get_object_or_404(User, id=author_id)
        subscription = Follow.objects.filter(user=user, author=author).first()
        if not subscription:
            return Response({'detail': 'Подписка не найдена.'},
                            status=status.HTTP_400_BAD_REQUEST)
        subscription.delete()
        return Response({'message': f'Вы отписались от {author.username}.'},
                        status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated],
        url_path='subscriptions',
        url_name='subscriptions',
    )
    def subscriptions(self, request):
        user = request.user
        subscribed_authors = Follow.objects.filter(user=user)
        paginated_authors = self.paginate_queryset(subscribed_authors)
        serializer = FollowSerializer(paginated_authors,
                                      many=True,
                                      context={'request': request})
        return self.get_paginated_response(serializer.data)
