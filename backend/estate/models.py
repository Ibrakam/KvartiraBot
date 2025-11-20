from django.db import models


class Apartment(models.Model):
    TYPE_CHOICES = [
        ('Новостройка', 'Новостройка'),
        ('Вторичное жильё', 'Вторичное жильё'),
    ]

    CONDITION_CHOICES = [
        ('С ремонтом', 'С ремонтом'),
        ('Без ремонта', 'Без ремонта'),
        ('Среднее состояние', 'Среднее состояние'),
    ]

    type = models.CharField(max_length=50, choices=TYPE_CHOICES, verbose_name='Тип')
    district = models.CharField(max_length=100, verbose_name='Район')
    condition = models.CharField(max_length=50, choices=CONDITION_CHOICES, verbose_name='Состояние')
    area = models.FloatField(verbose_name='Площадь (м²)')
    rooms = models.IntegerField(verbose_name='Количество комнат')
    price = models.IntegerField(verbose_name='Цена ($)')
    address = models.CharField(max_length=255, verbose_name='Адрес')
    orientation = models.CharField(max_length=255, verbose_name='Ориентир')
    floor = models.IntegerField(verbose_name='Этаж')
    floors_total = models.IntegerField(verbose_name='Всего этажей')
    description = models.TextField(blank=True, verbose_name='Описание')
    contact_name = models.CharField(max_length=100, verbose_name='Имя контакта')
    contact_phone = models.CharField(max_length=20, verbose_name='Телефон контакта')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'Квартира'
        verbose_name_plural = 'Квартиры'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.rooms}-комнатная квартира, {self.district}, ${self.price}"


class ApartmentImage(models.Model):
    apartment = models.ForeignKey(Apartment, related_name='images', on_delete=models.CASCADE, verbose_name='Квартира')
    image = models.ImageField(upload_to='apartments/', verbose_name='Изображение')
    order = models.IntegerField(default=0, verbose_name='Порядок')

    class Meta:
        verbose_name = 'Изображение квартиры'
        verbose_name_plural = 'Изображения квартир'
        ordering = ['order', 'id']

    def __str__(self):
        return f"Изображение {self.id} для квартиры {self.apartment.id}"



