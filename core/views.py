from django.shortcuts import render
from django.db.models import Q
from .models import Seminar


def cse_search(request):
    query = request.GET.get('q', '').strip()
    results = []
    error_message = None

    if 'q' in request.GET: 
        if not query:
            error_message = "Пожалуйста, введите запрос."
        elif len(query) < 3:
            error_message = "Введите минимум 3 символа."
        else:
            
            clean_query = query.replace('№', '').strip()
            results = Seminar.objects.filter(company='CSE').filter(
                Q(organization_name__iexact=query) |
                Q(registration_number__iexact=query) |  
                Q(certificates__full_name__iexact=query) |
                Q(certificates__certificate_number__endswith=clean_query)
            ).distinct()

       

    return render(request, 'cse_search.html', {
        'results': results,
        'query': query,
        'error_message': error_message
    })


def nika_search(request):
    query = request.GET.get('q', '').strip()
    results = []
    error_message = None

    if 'q' in request.GET:
        if not query:
            error_message = "Please enter a search query."
        elif len(query) < 3:
            error_message = "Please enter at least 3 characters."
        else:
            clean_query = query.replace('№', '').replace('No', '').strip()
            results = Seminar.objects.filter(company='NIKA').filter(
                Q(organization_name__iexact=query) |
                Q(registration_number__iexact=query) |
                Q(certificates__full_name__iexact=query) |
                Q(certificates__certificate_number__iexact=query)|
                Q(certificates__certificate_number__endswith=clean_query)
            ).distinct()

    return render(request, 'nika_search.html', {
        'results': results,
        'query': query,
        'error_message': error_message
    })