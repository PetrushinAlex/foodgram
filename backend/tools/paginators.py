from rest_framework.pagination import PageNumberPagination

from . import constants


class CustomRecipePaginator(PageNumberPagination):
    '''
    Кастомный пагинатор, устанавливающий по определенное в константе 
    количество объектов на страницу и позволяющий переопределить 
    это количество через параметр limit.
    '''

    page_size = constants.DEFAULT_PAGE_SIZE
    page_size_query_param = 'limit'
