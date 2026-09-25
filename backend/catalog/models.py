from django.db import models
from django.db.models import Q, F


class Category(models.Model):
    parent = models.ForeignKey(
        "Category",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="children",
    )
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Brand(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Product(models.Model):

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ACTIVE = "active", "Active"
        ARCHIVED = "archived", "Archived"

    brand = models.ForeignKey(
        "Brand",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class ProductCategory(models.Model):
    product = models.ForeignKey(
        "Product",
        on_delete=models.CASCADE
    )
    category = models.ForeignKey(
        "Category",
        on_delete=models.PROTECT
    )
    is_primary = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["product", "category"],
                name="unique_product_category"
            ),
            models.UniqueConstraint(
                fields=["product"],
                condition=Q(is_primary=True),
                name="unique_primary_category_per_product"
            ),
        ]


class ProductVariant(models.Model):
    product = models.ForeignKey(
        "Product",
        on_delete=models.CASCADE
    )
    sku = models.CharField(max_length=128, unique=True)
    barcode = models.CharField(max_length=64, null=True, blank=True, unique=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    compare_at_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(price__gte=0),
                name="price_gte_zero",
            ),
            models.CheckConstraint(
                condition=(
                        Q(compare_at_price__isnull=True) |
                        Q(compare_at_price__gte=F("price"))
                ),
                name="compare_price_gte_price",
            ),
            models.UniqueConstraint(
                fields=["product"],
                condition=Q(is_default=True),
                name="unique_default_variant_per_product",
            ),
        ]

    def __str__(self):
        return self.sku