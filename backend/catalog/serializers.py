from rest_framework import serializers

from .models import Category, Brand, Product, ProductVariant, ProductCategory


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


class BrandShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = (
            "id",
            "name",
            "slug",
        )


class ProductVariantShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = (
            "id",
            "sku",
            "price",
            "compare_at_price",
        )


class ProductListSerializer(serializers.ModelSerializer):
    brand = BrandShortSerializer(read_only=True)
    default_variant = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "slug",
            "brand",
            "default_variant",
        )

    def get_default_variant(self, obj):
        variant = obj.productvariant_set.filter(
            is_default=True,
            is_active=True,
        ).first()

        if variant is None:
            return None

        return ProductVariantShortSerializer(variant).data


class ProductCategorySerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="category.id", read_only=True)
    name = serializers.CharField(source="category.name", read_only=True)
    slug = serializers.CharField(source="category.slug", read_only=True)

    class Meta:
        model = ProductCategory
        fields = (
            "id",
            "name",
            "slug",
            "is_primary",
        )


class ProductVariantDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = (
            "id",
            "sku",
            "barcode",
            "price",
            "compare_at_price",
            "is_default",
            "sort_order",
        )


class ProductDetailSerializer(serializers.ModelSerializer):
    brand = BrandShortSerializer(read_only=True)

    categories = ProductCategorySerializer(
        source="productcategory_set",
        many=True,
        read_only=True,
    )

    variants = ProductVariantDetailSerializer(
        source="productvariant_set",
        many=True,
        read_only=True,
    )

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "slug",
            "description",
            "brand",
            "categories",
            "variants",
        )