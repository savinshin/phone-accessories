from rest_framework import viewsets

from .models import Category, Brand
from .serializers import CategorySerializer, BrandSerializer


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CategorySerializer
    lookup_field = "slug"

    queryset = Category.objects.filter(is_active=True).order_by("sort_order", "name")


class BrandViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = BrandSerializer
    lookup_field = "slug"

    queryset = Brand.objects.filter(is_active=True).order_by("name")