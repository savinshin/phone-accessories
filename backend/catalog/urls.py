from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import health_check, CategoryViewSet, BrandViewSet


router = DefaultRouter()

router.register('categories', CategoryViewSet, basename="category")
router.register('brands', BrandViewSet, basename="brand")

urlpatterns = [
    path('health/', health_check, name='health-check'),
    path('catalog/', include(router.urls))
]