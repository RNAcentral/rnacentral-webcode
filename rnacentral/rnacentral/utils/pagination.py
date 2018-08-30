from django.core.paginator import Paginator
from rest_framework.pagination import PageNumberPagination


class Pagination(PageNumberPagination):
    """
    DRF pagination_class, you use it by saying:

    class MyView(GenericAPIView):
        pagination_class = Pagination
    """
    page_size_query_param = 'page_size'


class RawQuerysetPaginator(Paginator):
    """
    This is a Django paginator, meant to adapt RawQueryset
    to DRF pagination classes.

    Stolen from:
    https://stackoverflow.com/questions/2532475/django-paginator-raw-sql-query
    """
    def __init__(self, object_list, per_page, count=1, **kwargs):
        super(RawQuerysetPaginator, self).__init__(object_list, per_page, **kwargs)
        self._raw_count = count

    @property
    def count(self):
        return self._raw_count

    def page(self, number):
        number = self.validate_number(number)
        return self._get_page(self.object_list, number, self)


class RawQuerysetPagination(Pagination):
    """
    DRF pagination_class for raw querysets.
    """
    django_paginator_class = RawQuerysetPaginator
