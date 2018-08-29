from django.core.paginator import Paginator
from rest_framework.pagination import PageNumberPagination


class Pagination(PageNumberPagination):
    """
    This is a DRF pagination_class, you use it by saying:

    class MyView(APIView):
        pagination_class = Pagination
    """
    page_size_query_param = 'page_size'


class RawPaginator(Paginator):
    """
    This is a Django paginator, meant to adapt RawQueryset
    to DRF pagination classes.

    Stolen from:
    https://stackoverflow.com/questions/2532475/django-paginator-raw-sql-query
    """
    def __init__(self, object_list, per_page, count, **kwargs):
        super(RawPaginator, self).__init__(object_list, per_page, **kwargs)
        self.raw_count = count

    def _get_count(self):
        return self.raw_count

    count = property(_get_count)

    def page(self, number):
        number = self.validate_number(number)
        return self._get_page(self.object_list, number, self)
