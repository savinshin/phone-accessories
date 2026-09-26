from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from catalog.models import Brand, Category


class Command(BaseCommand):
    help = "Seed local development categories and brands."

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

        with transaction.atomic():
            for name, slug, _ in brands:
                if Brand.objects.filter(name=name).exclude(slug=slug).exists():
                    raise CommandError(
                        f"Brand name {name!r} is already used by a different slug."
                    )

            Category.objects.update_or_create(
                slug="smartphones",
                defaults={
                    "name": "Smartphones",
                    "description": "Smartphones for everyday use.",
                    "parent": None,
                    "sort_order": 10,
                    "is_active": True,
                },
            )
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

            for name, slug, description, sort_order in children:
                Category.objects.update_or_create(
                    slug=slug,
                    defaults={
                        "name": name,
                        "description": description,
                        "parent": accessories,
                        "sort_order": sort_order,
                        "is_active": True,
                    },
                )

            for name, slug, description in brands:
                Brand.objects.update_or_create(
                    slug=slug,
                    defaults={
                        "name": name,
                        "description": description,
                        "is_active": True,
                    },
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Processed {len(children) + 2} categories and {len(brands)} brands."
            )
        )
