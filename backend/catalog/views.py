from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Category, Brand
from .serializers import CategorySerializer, BrandSerializer


@api_view(['GET'])
def health_check(request):
    return Response({'status': 'ok'})


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.filter(is_active=True).order_by('sort_order', 'name')
    lookup_field = 'slug'


class BrandViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = BrandSerializer
    queryset = Brand.objects.filter(is_active=True).order_by('name')
    lookup_field = 'slug'