from django.shortcuts import render
from django.db.models import Q
from .models import Seminar


def cse_search(request):
    if 'q' in request.GET:
        query = request.GET.get('q', '').strip()
        if not query:
            error_message = "Пожалуйста, введите запрос."
            results = []
        elif len(query) < 3:
            error_message = "Введите минимум 3 символа для поиска."
            results = []
        else:
            error_message = None
            results = Seminar.objects.filter(company='CSE').filter(
                Q(organization_name__icontains=query) |
                Q(registration_number__icontains=query) |
                Q(title__icontains=query) |
                Q(certificates__full_name__icontains=query) |
                Q(certificates__certificate_number__icontains=query)
            ).distinct()
    else:
        query = ''
        results = []
        error_message = None

    return render(request, 'cse_search.html', {
        'results': results,
        'query': query,
        'error_message': error_message
    })


def nika_search(request):
    if 'q' in request.GET:
        query = request.GET.get('q', '').strip()
        if not query:
            error_message = "Please enter a search query."
            results = []
        elif len(query) < 3:
            error_message = "Please enter at least 3 characters."
            results = []
        else:
            error_message = None
            results = Seminar.objects.filter(company='NIKA').filter(
                Q(organization_name__icontains=query) |
                Q(registration_number__icontains=query) |
                Q(title__icontains=query) |
                Q(certificates__full_name__icontains=query) |
                Q(certificates__certificate_number__icontains=query)
            ).distinct()
    else:
        query = ''
        results = []
        error_message = None

    return render(request, 'nika_search.html', {
        'results': results,
        'query': query,
        'error_message': error_message
    })
