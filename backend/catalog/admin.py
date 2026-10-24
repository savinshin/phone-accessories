from django.contrib import admin

from .models import Category, Brand, Product, ProductCategory, ProductVariant, Attribute, AttributeOption, \
    CategoryAttribute


class CategoryAttributeInline(admin.TabularInline):
    model = CategoryAttribute
    fields = ("attribute", "scope", "is_required", "is_filterable", "sort_order")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "parent", "slug", "is_active", "sort_order")
    search_fields = ("name", "slug")
    list_filter = ("is_active",)
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("sort_order", "name")
    inlines = [CategoryAttributeInline]


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active")
    search_fields = ("name", "slug")
    list_filter = ("is_active",)
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("name",)


class ProductCategoryInline(admin.TabularInline):
    model = ProductCategory


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "brand", "status", "slug", "created_at")
    search_fields = ("name", "slug")
    list_filter = ("status", "brand")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ProductCategoryInline, ProductVariantInline]


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ("sku", "product", "price", "is_active", "is_default")
    search_fields = ("sku", "barcode", "product__name")
    list_filter = ("is_active", "is_default")


class AttributeOptionInline(admin.TabularInline):
    model = AttributeOption
    fields = ("value", "is_active", "sort_order")


@admin.register(Attribute)
class AttributeAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "data_type", "unit", "is_active")
    search_fields = ("name", "slug")
    list_filter = ("data_type", "is_active")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [AttributeOptionInline]
