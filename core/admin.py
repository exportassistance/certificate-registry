from django.contrib import admin
from .models import Seminar, Certificate


class CertificateInline(admin.TabularInline):
    model = Certificate
    fields = ('full_name', 'order_number', 'certificate_number')
    readonly_fields = ('certificate_number',)


@admin.register(Seminar)
class SeminarAdmin(admin.ModelAdmin):
    list_display = ('title', 'organization_name', 'date_start', 'company')
    list_filter = ('company', 'date_start')
    search_fields = ('title', 'organization_name')
    inlines = [CertificateInline]


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'certificate_number', 'seminar')
    search_fields = ('full_name', 'certificate_number')
    list_filter = ('seminar__company',)
