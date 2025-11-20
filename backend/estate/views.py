from django.db.models import Q
from rest_framework import viewsets, filters
from .models import Apartment
from .serializers import ApartmentSerializer


class ApartmentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Apartment.objects.prefetch_related('images').all()
    serializer_class = ApartmentSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['address', 'district', 'description']
    ordering_fields = ['price', 'area', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Фильтрация по типу
        apartment_types = self.request.query_params.getlist('type')
        if apartment_types:
            queryset = queryset.filter(type__in=apartment_types)
        
        # Фильтрация по району
        districts = self.request.query_params.getlist('district')
        if districts:
            queryset = queryset.filter(district__in=districts)
        
        # Фильтрация по состоянию
        conditions = self.request.query_params.getlist('condition')
        if conditions:
            queryset = queryset.filter(condition__in=conditions)
        
        # Фильтрация по количеству комнат
        rooms = self.request.query_params.getlist('rooms')
        if rooms:
            try:
                room_values = [int(value) for value in rooms]
                queryset = queryset.filter(rooms__in=room_values)
            except ValueError:
                pass
        
        # Фильтрация по площади (несколько диапазонов)
        area_ranges = self.request.query_params.getlist('area_range')
        if area_ranges:
            area_q = Q()
            has_area_conditions = False
            for area_range in area_ranges:
                parts = area_range.split(':')
                if not parts:
                    continue
                area_min = float(parts[0]) if parts[0] else None
                area_max = float(parts[1]) if len(parts) > 1 and parts[1] else None
                range_q = Q()
                if area_min is not None:
                    range_q &= Q(area__gte=area_min)
                if area_max is not None:
                    range_q &= Q(area__lte=area_max)
                if range_q.children:
                    area_q |= range_q
                    has_area_conditions = True
            if has_area_conditions:
                queryset = queryset.filter(area_q)
        else:
            area_gte = self.request.query_params.get('area__gte', None)
            area_lte = self.request.query_params.get('area__lte', None)
            if area_gte:
                queryset = queryset.filter(area__gte=float(area_gte))
            if area_lte:
                queryset = queryset.filter(area__lte=float(area_lte))
        
        # Фильтрация по цене (несколько диапазонов)
        price_ranges = self.request.query_params.getlist('price_range')
        if price_ranges:
            price_q = Q()
            has_price_conditions = False
            for price_range in price_ranges:
                parts = price_range.split(':')
                if not parts:
                    continue
                price_min = int(float(parts[0])) if parts[0] else None
                price_max = int(float(parts[1])) if len(parts) > 1 and parts[1] else None
                range_q = Q()
                if price_min is not None:
                    range_q &= Q(price__gte=price_min)
                if price_max is not None:
                    range_q &= Q(price__lte=price_max)
                if range_q.children:
                    price_q |= range_q
                    has_price_conditions = True
            if has_price_conditions:
                queryset = queryset.filter(price_q)
        else:
            price_gte = self.request.query_params.get('price__gte', None)
            price_lte = self.request.query_params.get('price__lte', None)
            if price_gte:
                queryset = queryset.filter(price__gte=int(price_gte))
            if price_lte:
                queryset = queryset.filter(price__lte=int(price_lte))
        
        return queryset
