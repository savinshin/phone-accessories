from django.db.models import Prefetch
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Category, Brand, Product, ProductVariant, ProductCategory
from .serializers import CategorySerializer, BrandSerializer, ProductListSerializer, ProductDetailSerializer


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


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = "slug"

    queryset = (
        Product.objects.filter(status=Product.Status.ACTIVE)
        .select_related("brand")
        .prefetch_related(
            Prefetch(
                "productcategory_set",
                queryset=ProductCategory.objects.select_related("category"),
            ),
            Prefetch(
                "productvariant_set",
                queryset=ProductVariant.objects.filter(
                    is_active=True,
                ).order_by(
                    "sort_order",
                    "id",
                ),
            ),
        )
    )

    def get_serializer_class(self):
        if self.action == "list":
            return ProductListSerializer
        return ProductDetailSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        brand_slug = self.request.query_params.get("brand")
        if brand_slug:
            queryset = queryset.filter(
                brand__slug=brand_slug,
            )

        category_slug = self.request.query_params.get("category")
        if category_slug:
            queryset = queryset.filter(
                productcategory__category__slug=category_slug,
            )

        return queryset.distinct()