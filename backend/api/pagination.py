from rest_framework.pagination import PageNumberPagination


class StandardPagination(PageNumberPagination):
    """
    Кастомный класс пагинации для управления количеством объектов на странице.
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
