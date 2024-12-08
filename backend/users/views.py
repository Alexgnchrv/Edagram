from django.shortcuts import get_object_or_404

from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.pagination import StandardPagination
from api.serializers import FollowSerializer, StandartUserSerializer

from .models import Follow, User


class StandartUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = StandartUserSerializer
    pagination_class = StandardPagination

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated],
        url_path='subscribe',
        url_name='subscribe',
    )
    def manage_subscription(self, request, **kwargs):
        user = request.user
        author_id = self.kwargs.get('id')
        author = get_object_or_404(User, id=author_id)

        if request.method == 'POST':
            serializer = FollowSerializer(author,
                                          data=request.data,
                                          context={"request": request})
            serializer.is_valid(raise_exception=True)
            Follow.objects.create(user=user, author=author)
            return Response(f'Вы успешно подписались на {author.username}.',
                            status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            subscription = get_object_or_404(Follow, user=user, author=author)
            subscription.delete()
            return Response(f'Вы отписались от {author.username}.',
                            status=status.HTTP_204_NO_CONTENT)

        return Response({"detail": "Метод не поддерживается."},
                        status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated],
        url_path='subscriptions',
        url_name='subscriptions',
    )
    def list_subscriptions(self, request):
        user = request.user
        subscribed_authors = User.objects.filter(subscribers__user=user)

        paginated_authors = self.paginate_queryset(subscribed_authors)
        serializer = FollowSerializer(paginated_authors,
                                      many=True,
                                      context={'request': request})

        return self.get_paginated_response(serializer.data)
