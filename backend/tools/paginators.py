from rest_framework.pagination import PageNumberPagination

from . import constants as cnst


class CustomPaginator(PageNumberPagination):
    '''
    Кастомный пагинатор, устанавливающий по определенное в константе 
    количество объектов на страницу и позволяющий переопределить 
    это количество через параметр limit.
    '''

    page_size = cnst.DEFAULT_PAGE_SIZE
    page_size_query_param = 'limit'
