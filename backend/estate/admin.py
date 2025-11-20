from django.contrib import admin
from django.utils.html import format_html
from .models import Apartment, ApartmentImage


class ApartmentImageInline(admin.TabularInline):
    model = ApartmentImage
    extra = 1
    fields = ('image', 'order')


@admin.register(Apartment)
class ApartmentAdmin(admin.ModelAdmin):
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
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


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



