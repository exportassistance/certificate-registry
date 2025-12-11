from django.shortcuts import render
from django.db.models import Q
from .models import Seminar


def cse_search(request):
    query = request.GET.get('q', '').strip() 
    results = []

    if query:
        results = Seminar.objects.filter(company='CSE').filter(
            Q(organization_name__icontains=query) |
            Q(registration_number__icontains=query) |
            Q(title__icontains=query) |
            Q(certificates__full_name__icontains=query) |
            Q(certificates__certificate_number__icontains=query)
        ).distinct()

    return render(request, 'cse_search.html', {'results': results, 'query': query})


def nika_search(request):
    query = request.GET.get('q', '').strip()
    results = []

    if query:
        results = Seminar.objects.filter(company='NIKA').filter(
            Q(organization_name__icontains=query) |
            Q(registration_number__icontains=query) |
            Q(title__icontains=query) |
            Q(certificates__full_name__icontains=query) |
            Q(certificates__certificate_number__icontains=query)
        ).distinct()

    return render(request, 'nika_search.html', {'results': results, 'query': query})