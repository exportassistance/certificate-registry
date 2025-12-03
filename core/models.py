from django.db import models
from django.core.exceptions import ValidationError


class Seminar(models.Model):
    COMPANY_CHOICES = [
        ('CSE', 'ЦСЭ'),
        ('NIKA', 'NIKA'),
    ]

    company = models.CharField(
        max_length=10,
        choices=COMPANY_CHOICES,
        verbose_name="Тип реестра (Организация)",
        default='CSE'
    )

    organization_name = models.CharField(
        max_length=255,
        verbose_name="Наименование организации"
    )

    registration_number = models.CharField(
        max_length=50,
        verbose_name="УНП (Registration Number)"
    )

    title = models.CharField(
        max_length=255,
        verbose_name="Название семинара"
    )

    program = models.TextField(
        verbose_name="Программа семинара"
    )

    date_start = models.DateField(
        verbose_name="Дата начала"
    )

    date_end = models.DateField(
        null=True,
        blank=True,
        verbose_name="Дата окончания"
    )

    def __str__(self):
        return f"{self.date_start} | {self.organization_name} | {self.title}"

    class Meta:
        verbose_name = "Семинар"
        verbose_name_plural = "Семинары"


class Certificate(models.Model):
    seminar = models.ForeignKey(
        Seminar,
        on_delete=models.CASCADE,
        related_name='certificates',
        verbose_name="Семинар"
    )

    full_name = models.CharField(
        max_length=255,
        verbose_name="ФИО участника"
    )

    order_number = models.PositiveIntegerField(
        verbose_name="Порядковый номер",
        help_text="Целое число, уникальное в рамках семинара"
    )

    certificate_number = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Сгенерированный номер"
    )

    file_print = models.ImageField(
        upload_to='certificates/print/',
        null=True,
        blank=True,
        verbose_name="Файл для печати"
    )

    file_web = models.ImageField(
        upload_to='certificates/web/',
        null=True,
        blank=True,
        verbose_name="Файл для веб"
    )

    manual_upload = models.ImageField(
        upload_to='certificates/manual/',
        null=True,
        blank=True,
        verbose_name="Ручная загрузка (Скан)"
    )

    def __str__(self):
        return f"{self.full_name} ({self.certificate_number})"

    class Meta:
        verbose_name = "Сертификат"
        verbose_name_plural = "Сертификаты"
        unique_together = ['seminar', 'order_number']
