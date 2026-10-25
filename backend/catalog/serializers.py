from rest_framework import serializers

from .models import Category, Brand, Product, ProductVariant, ProductCategory, AttributeOption, CategoryAttribute, \
    Attribute


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


class AttributeOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttributeOption
        fields = (
            "id",
            "value",
            "sort_order",
        )


class CategoryAttributeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="attribute.id", read_only=True)
    name = serializers.CharField(source="attribute.name", read_only=True)
    slug = serializers.CharField(source="attribute.slug", read_only=True)
    data_type = serializers.CharField(source="attribute.data_type", read_only=True)
    unit = serializers.CharField(source="attribute.unit", read_only=True)

    options = serializers.SerializerMethodField()

    class Meta:
        model = CategoryAttribute
        fields = (
            "id",
            "name",
            "slug",
            "data_type",
            "unit",
            "scope",
            "is_required",
            "is_filterable",
            "sort_order",
            "options",
        )

    def get_options(self, obj):
        if obj.attribute.data_type != Attribute.DataType.OPTION:
            return []

        return AttributeOptionSerializer(
            obj.attribute.attributeoption_set.filter(
                is_active=True,
            ).order_by(
                "sort_order",
            ),
            many=True,
        ).data


class CategoryDetailSerializer(CategorySerializer):
    attributes = CategoryAttributeSerializer(
        source="categoryattribute_set",
        many=True,
        read_only=True,
    )

    class Meta(CategorySerializer.Meta):
        fields = CategorySerializer.Meta.fields + (
            "attributes",
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