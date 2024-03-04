from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models

from .manager import CustomUserManager


class CustomUser(AbstractUser):
    username = models.CharField(
        verbose_name='Логин',
        max_length=150,
        unique=True,
    )
    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        max_length=254,
        unique=True
    )
    first_name = models.CharField(
        verbose_name='Имя пользователя',
        max_length=150
    )
    last_name = models.CharField(
        verbose_name='Фамилия пользователя',
        max_length=150,
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    class Meta:
        ordering = ['username']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def clean(self):
        if self.username.lower() == 'me':
            raise ValidationError(
                'Указанное имя пользователя недопустимо'
            )


class Follow(models.Model):
    """Модель подписок на авторов."""

    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
                               related_name='user',
                               verbose_name='Пользователь')
    follower = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
                                 related_name='follower',
                                 verbose_name='Подписчик')

    class Meta:
        ordering = ['author']
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f"{self.follower.username} - подписчик {self.author.username}"
