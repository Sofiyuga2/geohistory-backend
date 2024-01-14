from datetime import datetime

from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models

from django.utils import timezone


class Pioneer(models.Model):
    STATUS_CHOICES = (
        (1, 'Действует'),
        (2, 'Удалена'),
    )

    status = models.IntegerField(choices=STATUS_CHOICES, default=1, verbose_name="Статус")
    name = models.CharField(max_length=100, verbose_name="Имя", blank=True, null=True)
    description = models.TextField(max_length=500, verbose_name="Биография", blank=True, null=True)
    image = models.ImageField(upload_to="pioneers", default="pioneers/default.jpg", verbose_name="Фото")
    date_birthday = models.IntegerField(verbose_name="Год рождения", blank=True, null=True)
    date_death = models.IntegerField(verbose_name="Год смерти", blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Первооткрыватель"
        verbose_name_plural = "Первооткрыватели"


class CustomUserManager(BaseUserManager):
    def create_user(self, name, email, password="1234", **extra_fields):
        extra_fields.setdefault('name', name)
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, name, email, password="1234", **extra_fields):
        extra_fields.setdefault('is_moderator', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(name, email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=30)
    is_moderator = models.BooleanField(default=False)

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


class Discovery(models.Model):
    STATUS_CHOICES = (
        (1, 'Введён'),
        (2, 'В работе'),
        (3, 'Завершён'),
        (4, 'Отменён'),
        (5, 'Удалён'),
    )

    name = models.CharField(max_length=100, verbose_name="Название", blank=True, null=True)
    description = models.TextField(max_length=500, verbose_name="Описание", blank=True, null=True)
    year = models.IntegerField(verbose_name="Год открытия", blank=True, null=True)

    verify = models.IntegerField(verbose_name="Результат проверки в архиве", default=-1, blank=True, null=True)

    pioneers = models.ManyToManyField(Pioneer, verbose_name="Первооткрыватели", null=True)
    status = models.IntegerField(choices=STATUS_CHOICES, default=1, verbose_name="Статус")
    date_created = models.DateTimeField(default=timezone.now(), verbose_name="Дата создания")
    date_formation = models.DateTimeField(verbose_name="Дата формирования", blank=True, null=True)
    date_complete = models.DateTimeField(verbose_name="Дата завершения", blank=True, null=True)

    owner = models.ForeignKey(CustomUser, on_delete=models.DO_NOTHING, verbose_name="Создатель", related_name='owner', null=True)
    moderator = models.ForeignKey(CustomUser, on_delete=models.DO_NOTHING, verbose_name="Модератор", related_name='moderator', null=True)

    def __str__(self):
        return "Открытие №" + str(self.pk)

    class Meta:
        verbose_name = "Открытие"
        verbose_name_plural = "Открытия"
        ordering = ('-date_formation', )