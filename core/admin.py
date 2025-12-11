from django.contrib import admin
from django.utils.html import format_html
from django.db import models
from django.forms import Textarea
from django.contrib import messages
from .models import Seminar, Certificate


@admin.action(description="🔄 Перегенерировать документы (PDF/JPG)")
def regenerate_certificates(modeladmin, request, queryset):
    count = 0
    for cert in queryset:

        if cert.file_print: cert.file_print.delete(save=False)
        if cert.file_web: cert.file_web.delete(save=False)
        if cert.preview_image: cert.preview_image.delete(save=False)

        cert.save()
        count += 1

    modeladmin.message_user(request, f"Обновлено сертификатов: {count}", messages.SUCCESS)


@admin.action(description="🔄 Обновить сертификаты всех участников")
def regenerate_seminar_certificates(modeladmin, request, queryset):
    total_certs = 0
    for seminar in queryset:
        certs = seminar.certificates.all()
        for cert in certs:
            if cert.file_print: cert.file_print.delete(save=False)
            if cert.file_web: cert.file_web.delete(save=False)
            if cert.preview_image: cert.preview_image.delete(save=False)
            cert.save()
            total_certs += 1

    modeladmin.message_user(request, f"Обработано семинаров: {queryset.count()}. Обновлено сертификатов: {total_certs}",
                            messages.SUCCESS)


class CertificateInline(admin.TabularInline):
    model = Certificate
    extra = 0
    fields = ('full_name', 'order_number', 'certificate_number')
    readonly_fields = ('certificate_number',)
    can_delete = True
    show_change_link = True


@admin.register(Seminar)
class SeminarAdmin(admin.ModelAdmin):
    list_display = ('date_start', 'title_short', 'organization_name', 'registration_number', 'company_badge',
                    'count_certificates')
    ordering = ('-date_start', 'company')
    search_fields = ('title', 'organization_name', 'registration_number', 'program')
    list_filter = ('company', 'date_start')
    inlines = [CertificateInline]

    # Добавляем действие сюда
    actions = [regenerate_seminar_certificates]

    formfield_overrides = {
        models.CharField: {'widget': Textarea(attrs={'rows': 2, 'cols': 80})},
        models.TextField: {'widget': Textarea(attrs={'rows': 10, 'cols': 80})},
    }

    def company_badge(self, obj):
        colors = {'CSE': 'red', 'NIKA': 'blue'}
        color = colors.get(obj.company, 'gray')
        return format_html(
            '<span style="color: white; background-color: {}; padding: 3px 10px; border-radius: 10px; font-weight: bold;">{}</span>',
            color, obj.get_company_display()
        )

    company_badge.short_description = "Реестр"
    company_badge.admin_order_field = 'company'

    def title_short(self, obj):
        return (obj.title[:50] + '...') if len(obj.title) > 50 else obj.title

    title_short.short_description = "Название семинара"

    def count_certificates(self, obj):
        return obj.certificates.count()

    count_certificates.short_description = "Участников"


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'company_badge', 'get_org_name', 'certificate_number', 'seminar_link', 'link_print',
                    'link_web')
    search_fields = ('full_name', 'certificate_number', 'seminar__title', 'seminar__organization_name')
    list_filter = ('seminar__company', 'seminar__date_start')

    # Добавляем действие сюда
    actions = [regenerate_certificates]

    fieldsets = (
        ("Информация об участнике", {
            'fields': ('seminar', 'full_name', 'order_number', 'certificate_number')
        }),
        ("Файлы", {
            'fields': ('preview_image', 'file_print', 'file_web', 'manual_upload'),
        }),
    )
    readonly_fields = ('certificate_number', 'file_print', 'file_web', 'preview_image')

    def company_badge(self, obj):
        colors = {'CSE': 'red', 'NIKA': 'blue'}
        color = colors.get(obj.seminar.company, 'gray')
        return format_html(
            '<span style="color: white; background-color: {}; padding: 3px 10px; border-radius: 10px; font-weight: bold;">{}</span>',
            color, obj.seminar.get_company_display()
        )

    company_badge.short_description = "Реестр"
    company_badge.admin_order_field = 'seminar__company'

    def get_org_name(self, obj):
        return obj.seminar.organization_name

    get_org_name.short_description = "Организация"
    get_org_name.admin_order_field = 'seminar__organization_name'

    def seminar_link(self, obj):
        return obj.seminar.title

    seminar_link.short_description = "Семинар"

    def link_print(self, obj):
        if obj.file_print:
            return format_html('<a href="{}" target="_blank">📄 PDF (Чистый)</a>', obj.file_print.url)
        return "-"

    link_print.short_description = "Печать"

    def link_web(self, obj):
        if obj.file_web:
            return format_html('<a href="{}" target="_blank">📄 PDF (С печатью)</a>', obj.file_web.url)
        return "-"

    link_web.short_description = "Клиент"
