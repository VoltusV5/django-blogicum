from django.core.paginator import Paginator

from .constants import PAGINATOR_ELEMENTS_IN_PAGE


def get_paginated_page(request, queryset, in_page=PAGINATOR_ELEMENTS_IN_PAGE):
    """
    Функция пагинации.
    Получает request
    Данные и кол-во элементов на странице
    """
    paginator = Paginator(queryset, in_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
