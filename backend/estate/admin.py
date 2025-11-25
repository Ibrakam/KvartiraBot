from django.contrib import admin
from django.utils.html import format_html
from django import forms
from django.db import models
from .models import Apartment, ApartmentImage


class MultipleFileInput(forms.ClearableFileInput):
    """Виджет для загрузки нескольких файлов"""
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    """Поле для загрузки нескольких файлов"""
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result


class ApartmentAdminForm(forms.ModelForm):
    """Форма админки с полем для множественной загрузки"""
    upload_images = MultipleFileField(
        label='Загрузить фотографии',
        required=False,
        help_text='Выберите несколько фотографий для загрузки (до 10 штук)'
    )

    class Meta:
        model = Apartment
        fields = '__all__'


class ApartmentImageInline(admin.TabularInline):
    model = ApartmentImage
    extra = 0
    fields = ('image', 'image_preview', 'order')
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="100" height="100" style="object-fit: cover;" />',
                obj.image.url
            )
        return "Нет изображения"
    image_preview.short_description = 'Превью'


@admin.register(Apartment)
class ApartmentAdmin(admin.ModelAdmin):
    form = ApartmentAdminForm
    list_display = ('id', 'rooms', 'district', 'price', 'area', 'type', 'condition', 'created_at')
    list_filter = ('type', 'condition', 'district', 'rooms')
    search_fields = ('address', 'district', 'contact_name', 'contact_phone')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [ApartmentImageInline]
    fieldsets = (
        ('Основная информация', {
            'fields': ('type', 'district', 'condition', 'rooms', 'area', 'price')
        }),
        ('Детали', {
            'fields': ('address', 'orientation', 'floor', 'floors_total', 'description')
        }),
        ('Контакты', {
            'fields': ('contact_name', 'contact_phone')
        }),
        ('Загрузка фотографий', {
            'fields': ('upload_images',),
            'description': 'Выберите несколько фотографий для загрузки сразу. Уже загруженные фото можно редактировать ниже.'
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        """Сохраняем квартиру и обрабатываем загруженные фотографии"""
        super().save_model(request, obj, form, change)

        # Обрабатываем множественную загрузку фотографий
        files = request.FILES.getlist('upload_images')
        if files:
            # Получаем максимальный порядковый номер существующих изображений
            max_order = ApartmentImage.objects.filter(apartment=obj).aggregate(
                max_order=models.Max('order')
            )['max_order'] or 0

            # Создаем новые изображения
            for idx, file in enumerate(files[:10]):  # Ограничиваем до 10 фото
                ApartmentImage.objects.create(
                    apartment=obj,
                    image=file,
                    order=max_order + idx + 1
                )

    class Media:
        css = {
            'all': ('admin/css/apartment_admin.css',)
        }
        js = ('admin/js/apartment_admin.js',)


@admin.register(ApartmentImage)
class ApartmentImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'apartment', 'order', 'image_preview')
    list_filter = ('apartment',)
    search_fields = ('apartment__id',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="100" style="object-fit: cover;" />', obj.image.url)
        return "Нет изображения"
    image_preview.short_description = 'Превью'




