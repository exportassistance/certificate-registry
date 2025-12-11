from django.db import models
from django.db.models import Max
from .utils import generate_certificates


class Seminar(models.Model):
    COMPANY_CHOICES = [
        ('CSE', 'ЦСЭ'),
        ('NIKA', 'NIKA'),
    ]
    company = models.CharField(max_length=10, choices=COMPANY_CHOICES, verbose_name="Тип реестра (Организация)",
                               default='CSE')
    organization_name = models.CharField(max_length=255, verbose_name="Наименование организации")
    registration_number = models.CharField(max_length=50, verbose_name="УНП (Registration Number)")
    title = models.CharField(max_length=142, verbose_name="Название семинара")
    program = models.TextField(verbose_name="Программа семинара")
    date_start = models.DateField(verbose_name="Дата начала")
    date_end = models.DateField(null=True, blank=True, verbose_name="Дата окончания")

    def __str__(self):
        return f"{self.date_start} | {self.organization_name} | {self.title}"

    class Meta:
        verbose_name = "Семинар"
        verbose_name_plural = "Семинары"


class Certificate(models.Model):
    seminar = models.ForeignKey(Seminar, on_delete=models.CASCADE, related_name='certificates', verbose_name="Семинар")
    full_name = models.CharField(max_length=255, verbose_name="ФИО участника")
    order_number = models.PositiveIntegerField(verbose_name="Порядковый номер", blank=True, null=True)
    certificate_number = models.CharField(max_length=50, blank=True, verbose_name="Сгенерированный номер")

    file_print = models.FileField(upload_to='certificates/print/', null=True, blank=True,
                                  verbose_name="PDF для печати (Без печати)")
    file_web = models.FileField(upload_to='certificates/web/', null=True, blank=True,
                                verbose_name="PDF для клиента (С печатью)")
    preview_image = models.ImageField(upload_to='certificates/previews/', null=True, blank=True,
                                      verbose_name="JPG Превью (Для сайта)")

    manual_upload = models.FileField(upload_to='certificates/manual/', null=True, blank=True,
                                     verbose_name="Ручная загрузка (Скан)")

    def __str__(self):
        return f"{self.full_name} ({self.certificate_number})"

    def save(self, *args, **kwargs):

        if not self.order_number:
            max_number = Certificate.objects.filter(seminar=self.seminar).aggregate(Max('order_number'))[
                'order_number__max']
            self.order_number = (max_number or 0) + 1

        if not self.certificate_number:
            target_date = self.seminar.date_end if self.seminar.date_end else self.seminar.date_start
            date_str = target_date.strftime('%d%m%Y')
            order_str = f"{self.order_number:02d}"
            self.certificate_number = f"№ {order_str}-{date_str}"

        if not self.file_print or not self.file_web or not self.preview_image:
            pdf_print, pdf_web, jpg_preview = generate_certificates(self)

            if pdf_print:
                self.file_print.save(pdf_print.name, pdf_print, save=False)
            if pdf_web:
                self.file_web.save(pdf_web.name, pdf_web, save=False)
            if jpg_preview:
                self.preview_image.save(jpg_preview.name, jpg_preview, save=False)

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Сертификат"
        verbose_name_plural = "Сертификаты"
        unique_together = ['seminar', 'order_number']
