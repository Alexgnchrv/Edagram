from rest_framework.pagination import PageNumberPagination

from recipes.constants import MAX_PAGE_SIZE, PAGE_SIZE


class StandardPagination(PageNumberPagination):
    """
    Кастомный класс пагинации для управления количеством объектов на странице.
    """

    page_size = PAGE_SIZE
    page_size_query_param = 'limit'
    max_page_size = MAX_PAGE_SIZE
