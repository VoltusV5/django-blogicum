from django.shortcuts import render


def csrf_failure(request, reason=''):
    """Обработка ошибки CSRF (403)"""
    return render(request, 'pages/403csrf.html', status=403)


def page_not_found(request, exception):
    """Обработка 404 ошибки"""
    return render(request, 'pages/404.html', status=404)


def server_error(request):
    """Обработка 500 ошибки"""
    return render(request, 'pages/500.html', status=500)
