from rest_framework import serializers
from .models import Apartment, ApartmentImage


class ApartmentImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ApartmentImage
        fields = ('id', 'image_url', 'order')

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            try:
                image_url = obj.image.url
                if image_url:
                    # Всегда возвращаем абсолютный URL
                    if request:
                        absolute_url = request.build_absolute_uri(image_url)
                        # Убеждаемся, что URL правильно сформирован
                        if absolute_url and absolute_url.startswith(('http://', 'https://')):
                            return absolute_url
                    # Если нет request, формируем URL вручную
                    # Используем настройки из settings
                    from django.conf import settings
                    if hasattr(settings, 'MEDIA_URL') and image_url.startswith(settings.MEDIA_URL):
                        # Если это медиа-файл, формируем полный URL
                        # В production нужно будет использовать реальный домен
                        host = request.get_host() if request else 'localhost:8000'
                        scheme = request.scheme if request else 'http'
                        return f"{scheme}://{host}{image_url}"
                    return image_url
            except (ValueError, AttributeError, Exception) as e:
                print(f"[ERROR] Ошибка при формировании URL изображения: {e}")
                pass
        return None


class ApartmentSerializer(serializers.ModelSerializer):
    images = ApartmentImageSerializer(many=True, read_only=True)

    class Meta:
        model = Apartment
        fields = (
            'id', 'type', 'district', 'condition', 'area', 'rooms',
            'price', 'address', 'orientation', 'floor', 'floors_total',
            'description', 'contact_name', 'contact_phone', 'images',
            'created_at', 'updated_at'
        )
        read_only_fields = ('created_at', 'updated_at')

