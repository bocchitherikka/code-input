from django.core.paginator import Paginator
from django.conf import settings


def paginator(request, posts):
    paginator_local_var = Paginator(posts, settings.ON_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator_local_var.get_page(page_number)
    return page_obj
