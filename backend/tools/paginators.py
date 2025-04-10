from rest_framework.pagination import PageNumberPagination


class CustomPaginator(PageNumberPagination):
    '''
    Кастомный пагинатор, устанавливающий по 6 объектов на страницу
    и позволяющий переопределить это количество через параметр limit.
    '''

    page_size = 6
    page_size_query_param = 'limit'
