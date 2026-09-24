from rest_framework import serializers

from .models import Category, Brand


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id',
                  'parent_id',
                  'name',
                  'slug',
                  'description',
                  'sort_order'
        )


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ('id',
                  'name',
                  'slug',
                  'description',
        )