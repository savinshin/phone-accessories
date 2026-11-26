from django.db import models
from django.db.models import F, Q
from django.core.exceptions import ValidationError


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
    status = models.CharField(max_length=20, choices=Status.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class ProductCategory(models.Model):
    product = models.ForeignKey("Product", on_delete=models.CASCADE)
    category = models.ForeignKey("Category", on_delete=models.PROTECT)
    is_primary = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["product", "category"],
                name="unique_product_category",
            ),
            models.UniqueConstraint(
                fields=["product"],
                condition=Q(is_primary=True),
                name="unique_primary_category_per_product",
            ),
        ]


class ProductVariant(models.Model):
    product = models.ForeignKey("Product", on_delete=models.CASCADE)
    sku = models.CharField(max_length=128, unique=True)
    barcode = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        unique=True,
    )
    price = models.DecimalField(max_digits=12, decimal_places=2)
    compare_at_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
    )
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
                    Q(compare_at_price__isnull=True)
                    | Q(compare_at_price__gte=F("price"))
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


class Attribute(models.Model):
    class DataType(models.TextChoices):
        TEXT = "text", "Text"
        INTEGER = "integer", "Integer"
        DECIMAL = "decimal", "Decimal"
        BOOLEAN = "boolean", "Boolean"
        OPTION = "option", "Option"

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    data_type = models.CharField(max_length=20, choices=DataType.choices)
    unit = models.CharField(max_length=64, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class AttributeOption(models.Model):
    attribute = models.ForeignKey("Attribute", on_delete=models.CASCADE)
    value = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["attribute", "value"],
                name="unique_attribute_value",
            ),
        ]


class CategoryAttribute(models.Model):
    class Scope(models.TextChoices):
        PRODUCT = "product", "Product"
        VARIANT = "variant", "Variant"

    category = models.ForeignKey("Category", on_delete=models.CASCADE)
    attribute = models.ForeignKey("Attribute", on_delete=models.PROTECT)
    scope = models.CharField(max_length=20, choices=Scope.choices)
    is_required = models.BooleanField(default=False)
    is_filterable = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["category", "attribute"],
                name="unique_category_attribute",
            ),
        ]


TYPED_VALUE_FIELDS = (
    "value_text",
    "value_integer",
    "value_decimal",
    "value_boolean",
    "option",
)


def exactly_one_value_check(name: str) -> models.CheckConstraint:
    branches = Q()

    for field in TYPED_VALUE_FIELDS:
        condition = Q(**{f"{field}__isnull": False})

        for other in TYPED_VALUE_FIELDS:
            if other != field:
                condition &= Q(**{f"{other}__isnull": True})

        branches |= condition

    return models.CheckConstraint(
        condition=branches,
        name=name,
    )


class TypedValueValidationMixin:
    EXPECTED_FIELDS = {
        Attribute.DataType.TEXT: "value_text",
        Attribute.DataType.INTEGER: "value_integer",
        Attribute.DataType.DECIMAL: "value_decimal",
        Attribute.DataType.BOOLEAN: "value_boolean",
        Attribute.DataType.OPTION: "option",
    }

    def clean(self):
        super().clean()

        if not self.attribute_id:
            return

        expected_field = self.EXPECTED_FIELDS[self.attribute.data_type]

        if getattr(self, expected_field) is None:
            raise ValidationError(
                {
                    expected_field: (
                        f"This field is required for "
                        f"{self.attribute.get_data_type_display().lower()} attributes."
                    )
                }
            )

        if (
            self.attribute.data_type == Attribute.DataType.OPTION
            and self.option is not None
            and self.option.attribute_id != self.attribute_id
        ):
            raise ValidationError(
                {
                    "option": (
                        "Selected option must belong to the selected attribute."
                    )
                }
            )


class ProductAttributeValue(TypedValueValidationMixin, models.Model):
    product = models.ForeignKey(
        "Product",
        on_delete=models.CASCADE,
        related_name="attribute_values",
    )
    attribute = models.ForeignKey(
        "Attribute",
        on_delete=models.PROTECT,
        related_name="product_values",
    )

    value_text = models.TextField(null=True, blank=True)
    value_integer = models.IntegerField(null=True, blank=True)
    value_decimal = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        null=True,
        blank=True,
    )
    value_boolean = models.BooleanField(null=True, blank=True)
    option = models.ForeignKey(
        "AttributeOption",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="product_values",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["product", "attribute"],
                name="unique_product_attribute_value",
            ),
            exactly_one_value_check("product_attribute_value_exactly_one_value"),
        ]


class VariantAttributeValue(TypedValueValidationMixin, models.Model):
    variant = models.ForeignKey(
        "ProductVariant",
        on_delete=models.CASCADE,
        related_name="attribute_values",
    )
    attribute = models.ForeignKey(
        "Attribute",
        on_delete=models.PROTECT,
        related_name="variant_values",
    )

    value_text = models.TextField(null=True, blank=True)
    value_integer = models.IntegerField(null=True, blank=True)
    value_decimal = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        null=True,
        blank=True,
    )
    value_boolean = models.BooleanField(null=True, blank=True)
    option = models.ForeignKey(
        "AttributeOption",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="variant_values",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["variant", "attribute"],
                name="unique_variant_attribute_value",
            ),
            exactly_one_value_check("variant_attribute_value_exactly_one_value"),
        ]