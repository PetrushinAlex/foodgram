from rest_framework.pagination import PageNumberPagination

from backend.food import constants as app_constants


class Paginator(PageNumberPagination):
    """
    Кастомный пагинатор для API с возможностью:
    - установки размера страницы по умолчанию из констант
    - динамического изменения размера страницы через параметр limit
    """

    page_size = app_constants.DEFAULT_PAGE_SIZE
    page_size_query_param = 'limit'
