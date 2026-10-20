from decimal import Decimal

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from catalog.models import Brand, Category, Product, ProductCategory, ProductVariant


class Command(BaseCommand):
    help = "Seed local development catalog data."

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError("seed_catalog is available only when DEBUG is True.")

        brands = (
            ("Apple", "apple", "Consumer technology from Apple."),
            ("Samsung", "samsung", "Consumer technology from Samsung."),
            ("Xiaomi", "xiaomi", "Consumer technology from Xiaomi."),
            ("Baseus", "baseus", "Device accessories from Baseus."),
            ("Anker", "anker", "Charging accessories from Anker."),
            ("UGREEN", "ugreen", "Connectivity accessories from UGREEN."),
            ("Spigen", "spigen", "Protective accessories from Spigen."),
            ("Belkin", "belkin", "Device accessories from Belkin."),
        )
        children = (
            ("Cases", "cases", "Protective cases for compatible devices.", 10),
            ("Chargers", "chargers", "Chargers for compatible devices.", 20),
            ("Cables", "cables", "Cables for charging and connecting devices.", 30),
            ("Power Banks", "power-banks", "Portable power for charging on the go.", 40),
            (
                "Screen Protectors",
                "screen-protectors",
                "Screen protectors for compatible devices.",
                50,
            ),
            ("Headphones", "headphones", "Headphones for personal listening.", 60),
        )
        products = (
            (
                "Demo Samsung Smartphone",
                "demo-samsung-smartphone",
                "A demo Samsung smartphone for local catalog development.",
                "samsung",
                "smartphones",
                (
                    (
                        "DEMO-SAMSUNG-SMARTPHONE-128",
                        Decimal("699.00"),
                        Decimal("749.00"),
                        True,
                        10,
                    ),
                    (
                        "DEMO-SAMSUNG-SMARTPHONE-256",
                        Decimal("799.00"),
                        None,
                        False,
                        20,
                    ),
                ),
            ),
            (
                "Demo Apple Smartphone",
                "demo-apple-smartphone",
                "A demo Apple smartphone for local catalog development.",
                "apple",
                "smartphones",
                (
                    (
                        "DEMO-APPLE-SMARTPHONE-128",
                        Decimal("899.00"),
                        None,
                        True,
                        10,
                    ),
                ),
            ),
            (
                "Demo Anker Charger",
                "demo-anker-charger",
                "A demo Anker charger for local catalog development.",
                "anker",
                "chargers",
                (
                    (
                        "DEMO-ANKER-CHARGER-20W",
                        Decimal("29.99"),
                        Decimal("39.99"),
                        True,
                        10,
                    ),
                ),
            ),
            (
                "Demo UGREEN Cable",
                "demo-ugreen-cable",
                "A demo UGREEN cable for local catalog development.",
                "ugreen",
                "cables",
                (
                    (
                        "DEMO-UGREEN-CABLE-USB-C",
                        Decimal("12.99"),
                        None,
                        True,
                        10,
                    ),
                ),
            ),
            (
                "Demo Generic Case",
                "demo-generic-case",
                "A demo generic case for local catalog development.",
                None,
                "cases",
                (
                    (
                        "DEMO-GENERIC-CASE",
                        Decimal("19.99"),
                        None,
                        True,
                        10,
                    ),
                ),
            ),
            (
                "Demo Xiaomi Power Bank",
                "demo-xiaomi-power-bank",
                "A demo Xiaomi power bank for local catalog development.",
                "xiaomi",
                "power-banks",
                (
                    (
                        "DEMO-XIAOMI-POWER-BANK-10000",
                        Decimal("29.99"),
                        None,
                        False,
                        10,
                    ),
                    (
                        "DEMO-XIAOMI-POWER-BANK-20000",
                        Decimal("39.99"),
                        None,
                        False,
                        20,
                    ),
                ),
            ),
        )

        with transaction.atomic():
            for name, slug, _ in brands:
                if Brand.objects.filter(name=name).exclude(slug=slug).exists():
                    raise CommandError(
                        f"Brand name {name!r} is already used by a different slug."
                    )

            for _, product_slug, _, _, category_slug, variants in products:
                for sku, _, _, _, _ in variants:
                    if ProductVariant.objects.filter(sku=sku).exclude(
                        product__slug=product_slug
                    ).exists():
                        raise CommandError(
                            f"SKU {sku!r} is already used by a different product."
                        )

                if ProductCategory.objects.filter(
                    product__slug=product_slug,
                    is_primary=True,
                ).exclude(category__slug=category_slug).exists():
                    raise CommandError(
                        f"Product {product_slug!r} already has a different primary category."
                    )

                default_sku = next(
                    (sku for sku, _, _, is_default, _ in variants if is_default),
                    None,
                )
                if default_sku:
                    if ProductVariant.objects.filter(
                        product__slug=product_slug,
                        is_default=True,
                    ).exclude(sku=default_sku).exists():
                        raise CommandError(
                            f"Product {product_slug!r} already has a different default SKU."
                        )
                elif product_slug == "demo-xiaomi-power-bank" and ProductVariant.objects.filter(
                    product__slug=product_slug,
                    is_default=True,
                ).exists():
                    raise CommandError(
                        "Product 'demo-xiaomi-power-bank' must not have a default SKU."
                    )

            categories = {}
            smartphones, _ = Category.objects.update_or_create(
                slug="smartphones",
                defaults={
                    "name": "Smartphones",
                    "description": "Smartphones for everyday use.",
                    "parent": None,
                    "sort_order": 10,
                    "is_active": True,
                },
            )
            categories["smartphones"] = smartphones
            accessories, _ = Category.objects.update_or_create(
                slug="accessories",
                defaults={
                    "name": "Accessories",
                    "description": "Accessories for personal devices.",
                    "parent": None,
                    "sort_order": 20,
                    "is_active": True,
                },
            )
            categories["accessories"] = accessories

            for name, slug, description, sort_order in children:
                category, _ = Category.objects.update_or_create(
                    slug=slug,
                    defaults={
                        "name": name,
                        "description": description,
                        "parent": accessories,
                        "sort_order": sort_order,
                        "is_active": True,
                    },
                )
                categories[slug] = category

            brand_objects = {}
            for name, slug, description in brands:
                brand, _ = Brand.objects.update_or_create(
                    slug=slug,
                    defaults={
                        "name": name,
                        "description": description,
                        "is_active": True,
                    },
                )
                brand_objects[slug] = brand

            for name, slug, description, brand_slug, category_slug, variants in products:
                product, _ = Product.objects.update_or_create(
                    slug=slug,
                    defaults={
                        "name": name,
                        "description": description,
                        "brand": brand_objects[brand_slug] if brand_slug else None,
                        "status": Product.Status.ACTIVE,
                    },
                )
                ProductCategory.objects.update_or_create(
                    product=product,
                    category=categories[category_slug],
                    defaults={"is_primary": True},
                )

                for sku, price, compare_at_price, is_default, sort_order in variants:
                    ProductVariant.objects.update_or_create(
                        sku=sku,
                        defaults={
                            "product": product,
                            "price": price,
                            "compare_at_price": compare_at_price,
                            "is_active": True,
                            "is_default": is_default,
                            "sort_order": sort_order,
                        },
                    )

        self.stdout.write(
            self.style.SUCCESS(
                "Processed "
                f"{len(children) + 2} categories, {len(brands)} brands, "
                f"{len(products)} products, {len(products)} product categories, and "
                f"{sum(len(variants) for _, _, _, _, _, variants in products)} product variants."
            )
        )
