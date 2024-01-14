from datetime import datetime

from django.db import models, connection

from django.urls import reverse
from django.utils import timezone


class Pioneer(models.Model):
    STATUS_CHOICES = (
        (1, 'Действует'),
        (2, 'Удалена'),
    )

    name = models.CharField(max_length=100, verbose_name="Имя")
    status = models.IntegerField(max_length=100, choices=STATUS_CHOICES, default=1, verbose_name="Статус")
    description = models.TextField(max_length=500, verbose_name="Биография")
    image = models.ImageField(upload_to="pioneers", default="pioneers/default.jpg", verbose_name="Фото")
    date_birthday = models.IntegerField(default=1800, verbose_name="Год рождения")
    date_death = models.IntegerField(default=1900, verbose_name="Год смерти")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Первооткрыватель"
        verbose_name_plural = "Первооткрыватели"

    def get_absolute_url(self):
        return reverse("pioneer_details", kwargs={"pioneer_id": self.id})

    def get_delete_url(self):
        return reverse("pioneer_delete", kwargs={"pioneer_id": self.id})

    def delete(self):
        with connection.cursor() as cursor:
            cursor.execute("UPDATE discoveries_pioneer SET status = 2 WHERE id = %s", [self.pk])


class Discovery(models.Model):
    STATUS_CHOICES = (
        (1, 'Введён'),
        (2, 'В работе'),
        (3, 'Завершён'),
        (4, 'Отменён'),
        (5, 'Удалён'),
    )

    date = models.DateField(default=datetime.now(tz=timezone.utc), verbose_name="Год открытия")

    status = models.IntegerField(max_length=100, choices=STATUS_CHOICES, default=1, verbose_name="Статус")
    date_created = models.DateTimeField(default=datetime.now(tz=timezone.utc), verbose_name="Дата создания")
    date_of_formation = models.DateTimeField(default=datetime.now(tz=timezone.utc), verbose_name="Дата формирования")
    date_complete = models.DateTimeField(default=datetime.now(tz=timezone.utc), verbose_name="Дата завершения")

    def __str__(self):
        return "Открытие №" + str(self.pk)

    class Meta:
        verbose_name = "Открытие"
        verbose_name_plural = "Открытия"