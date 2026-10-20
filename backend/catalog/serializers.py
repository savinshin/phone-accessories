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
        for variant in obj.productvariant_set.all():
            if variant.is_default:
                return ProductVariantShortSerializer(variant).data

        return None


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
    default_variant = serializers.SerializerMethodField()

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
            "default_variant",
            "categories",
            "variants",
        )

    def get_default_variant(self, obj):
        for variant in obj.productvariant_set.all():
            if variant.is_default:
                return ProductVariantShortSerializer(variant).data

        return None