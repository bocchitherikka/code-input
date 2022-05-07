from django.utils import timezone


def year(request):
    present_year = timezone.now().year
    return {'year': present_year}
