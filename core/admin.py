from django.contrib import admin
from django.utils.html import format_html
from django.db import models
from django.forms import Textarea
from django.contrib import messages
from .models import Seminar, Certificate
from django.urls import reverse

def get_company_badge(company_code, company_label):
    colors = {'CSE': '#b40000', 'NIKA': '#004099'}
    bg_color = colors.get(company_code, 'gray')
    return format_html(
        '<span style="color: white; background-color: {}; padding: 4px 10px; border-radius: 12px; font-weight: bold; font-size: 11px;">{}</span>',
        bg_color, company_label
    )


@admin.action(description="⚡ Перегенерировать документы (PDF/JPG)")
def regenerate_certificates(modeladmin, request, queryset):
    count = 0
    for cert in queryset:
        if cert.manual_upload and cert.manual_upload.name:
            continue

        if cert.file_print: cert.file_print.delete(save=False)
        if cert.file_web: cert.file_web.delete(save=False)
        if cert.preview_image: cert.preview_image.delete(save=False)

        cert.file_print = None
        cert.file_web = None
        cert.preview_image = None

        cert.save()
        count += 1
    modeladmin.message_user(request, f"Успешно обновлено сертификатов: {count}", messages.SUCCESS)


@admin.action(description="⚡ Обновить сертификаты всех участников")
def regenerate_seminar_certificates(modeladmin, request, queryset):
    total = 0
    for seminar in queryset:
        certs = seminar.certificates.all()
        for cert in certs:
            if cert.manual_upload and cert.manual_upload.name:
                continue

            if cert.file_print: cert.file_print.delete(save=False)
            if cert.file_web: cert.file_web.delete(save=False)
            if cert.preview_image: cert.preview_image.delete(save=False)

            cert.file_print = None
            cert.file_web = None
            cert.preview_image = None
            cert.save()
            total += 1
    modeladmin.message_user(request, f"Семинаров обработано: {queryset.count()}. Сертификатов обновлено: {total}",
                            messages.SUCCESS)


class CertificateInline(admin.TabularInline):
    model = Certificate
    extra = 0
    fields = ('full_name', 'certificate_number', 'manual_upload', 'link_files')
    readonly_fields = ('certificate_number','link_files')
    can_delete = True
    show_change_link = True
    verbose_name = "Участник"
    verbose_name_plural = "Список участников"

    def link_files(self, obj):
        links = []
        if obj.file_print:
            links.append(f'<a href="{obj.file_print.url}" target="_blank" style="color:white;">📄 PDF(чистый) </a>')
        if obj.file_web:
            links.append(
                f'<a href="{obj.file_web.url}" target="_blank" style="color:green; font-weight:bold;">📥 PDF(c печатью) </a>')

        if not links: return "-"
        return format_html(" | ".join(links))

    link_files.short_description = "Скачать"


@admin.register(Seminar)
class SeminarAdmin(admin.ModelAdmin):
    list_display = ('date_start', 'display_company', 'organization_name', 'registration_number', 'display_title',
                    'display_count')
    list_display_links = ('date_start', 'display_title')
    
    ordering = ('-date_start', 'company')

    search_fields = ('title', 'organization_name', 'registration_number', 'program')
    list_filter = ('company', 'date_start')

    inlines = [CertificateInline]
    actions = [regenerate_seminar_certificates]

    formfield_overrides = {
        models.CharField: {'widget': Textarea(attrs={'rows': 2, 'cols': 90, 'style': 'resize:vertical;'})},
        models.TextField: {'widget': Textarea(attrs={'rows': 15, 'cols': 90, 'style': 'resize:vertical;'})},
    }

    def display_company(self, obj):
        return get_company_badge(obj.company, obj.get_company_display())

    display_company.short_description = "Реестр"
    display_company.admin_order_field = 'company'

    def display_title(self, obj):
        return (obj.title[:60] + '...') if len(obj.title) > 60 else obj.title

    display_title.short_description = "Название семинара"

    def display_count(self, obj):
        count = obj.certificates.count()
        return format_html(f'<b>{count}</b> чел.')

    display_count.short_description = "Участников"


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('display_date', 'display_company', 'display_org', 'display_unp', 'display_seminar', 'full_name',
                    'certificate_number','link_print', 'link_web')
    list_display_links = ('full_name',)

    search_fields = ('full_name', 'certificate_number', 'seminar__title', 'seminar__organization_name',
                     'seminar__registration_number')
    list_filter = ('seminar__company', 'seminar__date_start')

    actions = [regenerate_certificates]

    fieldsets = (
        ("Информация об участнике", {
            'fields': ('seminar', 'full_name', 'certificate_number')
        }),
        ("Ручная загрузка (Архив)", {
            'fields': ('manual_upload',),
            'description': 'Загрузите сюда PDF, чтобы отключить авто-генерацию для этого человека.'
        }),
        ("Файлы системы (Только чтение)", {
            'fields': ('preview_image', 'file_print', 'file_web'),
        }),
    )
    readonly_fields = ('certificate_number', 'file_print', 'file_web', 'preview_image', 'seminar')

    def has_add_permission(self, request):
        return False

    def display_date(self, obj):
        return obj.seminar.date_start

    display_date.short_description = "Дата"
    display_date.admin_order_field = 'seminar__date_start'

    def display_company(self, obj):
        return get_company_badge(obj.seminar.company, obj.seminar.get_company_display())

    display_company.short_description = "Реестр"
    display_company.admin_order_field = 'seminar__company'

    def display_org(self, obj):
        return obj.seminar.organization_name

    display_org.short_description = "Организация"
    display_org.admin_order_field = 'seminar__organization_name'

    def display_unp(self, obj):
        return obj.seminar.registration_number

    display_unp.short_description = "УНП"
    display_unp.admin_order_field = 'seminar__registration_number'

    def display_seminar(self, obj):
        title = obj.seminar.title
        short_title = (title[:30] + '...') if len(title) > 30 else title
        url = reverse("admin:core_seminar_change", args=[obj.seminar.id])
        return format_html('<a href="{}" title="Редактировать семинар">{}</a>', url, short_title)

    display_seminar.short_description = "Семинар (Ред.)"
    display_seminar.admin_order_field = 'seminar__title'

    def link_print(self, obj):
        if obj.file_print:
            return format_html('<a href="{}" target="_blank" style="color:white;">📄 Чистый</a>', obj.file_print.url)
        return "—"

    link_print.short_description = "Без печати"

    def link_web(self, obj):
        url = obj.file_web.url if obj.file_web else (obj.manual_upload.url if obj.manual_upload else None)
        if url:
            return format_html('<a href="{}" target="_blank" style="color: green; font-weight: bold;">📥 Клиент</a>',
                               url)
        return "—"

    link_web.short_description = "С печатью"
