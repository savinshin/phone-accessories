# Phone Accessories — Catalog Domain Schema

**Project:** `phone-accessories`  
**Document status:** approved catalog design, not necessarily implemented yet  
**Last updated:** 2026-09-16

This document is the source of truth for the currently agreed catalog-domain design.

It describes the target schema and domain rules for:

- Category
- Brand
- Product
- ProductCategory
- ProductVariant
- Attribute
- AttributeOption
- CategoryAttribute
- ProductAttributeValue
- VariantAttributeValue
- ProductMedia
- Stock
- ProductCompatibility

Do not implement additional catalog entities or change the decisions below without a separate design discussion.

---

## 1. General principles

- Do not create separate `Phone`, `Laptop`, `Accessory`, etc. product tables.
- Use one universal product model.
- `Product` is the conceptual product/model.
- `ProductVariant` is the concrete sellable SKU.
- Price and stock belong to `ProductVariant`.
- Product characteristics use an extensible attribute system.
- Do not model filterable characteristics as fixed columns such as `processor`, `battery`, `material`, etc.
- Do not store the main filterable characteristics in one JSON field.
- Categories support hierarchy.
- Significant schema changes must be designed before implementation.
- Prefer database constraints for invariants that PostgreSQL can enforce reliably.
- Cross-table invariants that cannot be expressed cleanly as database checks must be validated in Django.
- Normal catalog lifecycle should prefer deactivation/archiving over destructive deletion.

---

# 2. Category

## Fields

| Field | Type / rule |
|---|---|
| `id` | PK |
| `parent_id` | FK -> `Category`, nullable |
| `name` | varchar, required |
| `slug` | varchar, required, globally unique |
| `description` | text, optional |
| `is_active` | boolean, default `true` |
| `sort_order` | non-negative integer, default `0` |
| `created_at` | datetime |
| `updated_at` | datetime |

## Rules

`parent_id` implements an adjacency-list hierarchy.

Example:

```text
Accessories
├── Cases
│   ├── Phone Cases
│   └── Tablet Cases
├── Chargers
└── Cables
```

Root categories have `parent_id = NULL`.

Parent deletion uses `PROTECT`. A category tree must not disappear accidentally through cascade deletion.

`slug` is globally unique.

`sort_order` controls explicit catalog/menu ordering.

Do not add tree libraries such as MPTT unless a real performance or query requirement appears.

## Not included yet

- image
- icon
- SEO fields
- cached product count
- level
- materialized path

---

# 3. Brand

## Fields

| Field | Type / rule |
|---|---|
| `id` | PK |
| `name` | varchar, required, unique |
| `slug` | varchar, required, unique |
| `description` | text, optional |
| `is_active` | boolean, default `true` |
| `created_at` | datetime |
| `updated_at` | datetime |

## Rules

Brand represents the manufacturer/brand, not catalog taxonomy.

Example:

```text
Category = Smartphones
Brand = Apple
```

Do not create categories such as `Apple Smartphones` merely to represent a brand.

There is no direct `Category <-> Brand` relation. They meet through `Product`.

## Not included yet

- logo
- website
- country
- featured flag
- explicit sort order

Brand media may be added later together with the storage/media work.

---

# 4. Product

## Fields

| Field | Type / rule |
|---|---|
| `id` | PK |
| `brand_id` | FK -> `Brand`, nullable |
| `name` | varchar, required |
| `slug` | varchar, required, unique |
| `description` | text, optional |
| `status` | enum, required |
| `created_at` | datetime |
| `updated_at` | datetime |

## Status values

```text
draft
active
archived
```

Meaning:

- `draft` — being prepared, not customer-visible.
- `active` — published/available for catalog use.
- `archived` — retained historically but no longer actively sold/published.

## Rules

`brand_id` is nullable because generic/unbranded products may exist.

Brand deletion uses `PROTECT` while products reference it.

`Product` does not contain price, stock, color, storage, processor, battery, etc.

A sellable product is expected to have at least one `ProductVariant`, but that requirement is not forced by a simple database constraint because drafts may temporarily be incomplete.

---

# 5. ProductCategory

Explicit through model between `Product` and `Category`.

## Fields

| Field | Type / rule |
|---|---|
| `id` | PK |
| `product_id` | FK -> `Product` |
| `category_id` | FK -> `Category` |
| `is_primary` | boolean, default `false` |

## Constraints

```text
UNIQUE(product_id, category_id)
```

At most one primary category per product:

```text
UNIQUE(product_id) WHERE is_primary = true
```

## Rules

A product may belong to multiple categories.

`is_primary` identifies the canonical/main category for uses such as breadcrumbs and primary catalog placement.

Deletion behavior:

```text
product  -> CASCADE
category -> PROTECT
```

Draft/incomplete products may temporarily have no primary category. Publication rules can enforce stronger requirements later at the application level.

---

# 6. ProductVariant

Concrete sellable SKU.

## Fields

| Field | Type / rule |
|---|---|
| `id` | PK |
| `product_id` | FK -> `Product` |
| `sku` | varchar, required, unique |
| `barcode` | varchar, nullable, unique when present |
| `price` | decimal, required |
| `compare_at_price` | decimal, nullable |
| `is_active` | boolean, default `true` |
| `is_default` | boolean, default `false` |
| `sort_order` | non-negative integer, default `0` |
| `created_at` | datetime |
| `updated_at` | datetime |

Recommended price precision:

```text
max_digits = 12
decimal_places = 2
```

## Constraints

```text
price >= 0
```

```text
compare_at_price IS NULL
OR compare_at_price >= price
```

At most one default variant per product:

```text
UNIQUE(product_id) WHERE is_default = true
```

`barcode` is nullable. Missing barcode should be represented by `NULL`, not by repeated empty-string values.

## Rules

Every sellable product uses variants, even when the customer sees no variant selector.

Example:

```text
Product:
Baseus USB-C Cable 1m

Variant:
SKU = BASEUS-CABLE-1M
price = 9.99
```

Do not create a second pricing path where products without visible variants store price directly on `Product`.

`is_active = false` means the SKU is not offered.

`stock = 0` means the SKU is offered but currently unavailable. These are different concepts.

`product_id` deletion behavior: `CASCADE`.

## Not included yet

- currency per variant
- color/storage/size/material fixed columns
- stock quantity directly on the variant
- weight/dimensions unless a real shipping requirement is designed

The store is currently treated as single-currency. Multi-currency is a separate architecture decision.

---

# 7. Attribute

Definition of a reusable product characteristic.

## Fields

| Field | Type / rule |
|---|---|
| `id` | PK |
| `name` | varchar, required |
| `slug` | varchar, required, unique |
| `data_type` | enum, required |
| `unit` | varchar, optional |
| `is_active` | boolean, default `true` |
| `created_at` | datetime |
| `updated_at` | datetime |

## Supported data types

```text
text
integer
decimal
boolean
option
```

Examples:

| Attribute | Type | Unit |
|---|---|---|
| Processor | text | — |
| Screen Size | decimal | inch |
| Battery Capacity | integer | mAh |
| RAM | integer | GB |
| Color | option | — |
| Storage | option | GB |
| MagSafe | boolean | — |
| Power | integer | W |

`slug` is the stable technical identifier.

Units are stored separately from values, so numeric values remain numeric and filterable.

Example:

```text
Battery Capacity:
value = 5000
unit = mAh
```

not:

```text
"5000 mAh"
```

---

# 8. AttributeOption

Allowed option for an `Attribute` whose `data_type = option`.

## Fields

| Field | Type / rule |
|---|---|
| `id` | PK |
| `attribute_id` | FK -> `Attribute` |
| `value` | varchar, required |
| `is_active` | boolean, default `true` |
| `sort_order` | non-negative integer, default `0` |
| `created_at` | datetime |
| `updated_at` | datetime |

## Constraint

```text
UNIQUE(attribute_id, value)
```

Examples:

```text
Color:
- Black
- White
- Blue
```

```text
Storage:
- 128
- 256
- 512
```

An option can be deactivated without deleting historical references.

Deletion of an option already used by attribute values should be protected.

---

# 9. CategoryAttribute

Defines how an attribute is used in a specific category.

## Fields

| Field | Type / rule |
|---|---|
| `id` | PK |
| `category_id` | FK -> `Category` |
| `attribute_id` | FK -> `Attribute` |
| `scope` | enum: `product` / `variant` |
| `is_required` | boolean, default `false` |
| `is_filterable` | boolean, default `false` |
| `sort_order` | non-negative integer, default `0` |

## Constraint

```text
UNIQUE(category_id, attribute_id)
```

## Example

For `Smartphones`:

| Attribute | Scope | Required | Filterable |
|---|---|---:|---:|
| Processor | product | yes | yes |
| Screen Size | product | yes | yes |
| Battery Capacity | product | no | yes |
| Color | variant | yes | yes |
| Storage | variant | yes | yes |

For `Cases`:

| Attribute | Scope | Required | Filterable |
|---|---|---:|---:|
| Material | product | yes | yes |
| MagSafe | product | no | yes |
| Color | variant | yes | yes |

## Rules

Do not put global flags such as `Attribute.is_variant_attribute` or global `Attribute.is_filterable`.

The usage belongs to the category context.

Automatic parent-category attribute inheritance is not implemented.

Category attributes are explicit.

If a product belongs to multiple categories, overlapping category-attribute definitions must remain compatible. Conflicting scope/meaning across those categories is an invalid catalog configuration and should be prevented/validated at the application level when that workflow is implemented.

---

# 10. ProductAttributeValue

Typed value for a product-level attribute.

## Fields

| Field | Type / rule |
|---|---|
| `id` | PK |
| `product_id` | FK -> `Product` |
| `attribute_id` | FK -> `Attribute` |
| `value_text` | nullable |
| `value_integer` | nullable |
| `value_decimal` | nullable |
| `value_boolean` | nullable |
| `option_id` | FK -> `AttributeOption`, nullable |

## Constraint

```text
UNIQUE(product_id, attribute_id)
```

Exactly one typed value column must be populated.

Examples:

```text
Processor:
value_text = "A18 Pro"
```

```text
Screen Size:
value_decimal = 6.3
```

```text
MagSafe:
value_boolean = true
```

```text
Material:
option_id -> Silicone
```

## Validation

Database constraints should enforce that exactly one typed value field is set.

Django validation must enforce cross-table rules that normal PostgreSQL checks cannot express cleanly:

- selected typed field matches `Attribute.data_type`;
- `option_id` belongs to the same `Attribute`.

Attribute deletion while values reference it uses `PROTECT`.

---

# 11. VariantAttributeValue

Typed value for a variant-level attribute.

## Fields

| Field | Type / rule |
|---|---|
| `id` | PK |
| `variant_id` | FK -> `ProductVariant` |
| `attribute_id` | FK -> `Attribute` |
| `value_text` | nullable |
| `value_integer` | nullable |
| `value_decimal` | nullable |
| `value_boolean` | nullable |
| `option_id` | FK -> `AttributeOption`, nullable |

## Constraint

```text
UNIQUE(variant_id, attribute_id)
```

Exactly one typed value field must be populated.

The same type and option validation rules as `ProductAttributeValue` apply.

Example:

```text
Variant SKU: IP16P-256-BLK

Storage = 256 GB
Color = Black
```

---

# 12. ProductMedia

Media associated with a product and optionally a specific variant.

Current use case is product images.

## Fields

| Field | Type / rule |
|---|---|
| `id` | PK |
| `product_id` | FK -> `Product` |
| `variant_id` | FK -> `ProductVariant`, nullable |
| `file` | Django `ImageField` / storage-backed file |
| `alt_text` | varchar, optional |
| `sort_order` | non-negative integer, default `0` |
| `is_primary` | boolean, default `false` |
| `created_at` | datetime |
| `updated_at` | datetime |

## Rules

If `variant_id = NULL`, media belongs to the general product.

If `variant_id` is present, `variant.product_id` must equal `product_id`.

This is a cross-table invariant and is validated in Django.

`product_id` is intentionally retained even when a variant is set so all product media can be queried directly.

At most one general primary image per product:

```text
UNIQUE(product_id)
WHERE is_primary = true
AND variant_id IS NULL
```

At most one primary image per variant:

```text
UNIQUE(variant_id)
WHERE is_primary = true
```

Deletion behavior:

```text
product -> CASCADE
variant -> CASCADE
```

Database-row deletion must not assume direct filesystem semantics. Physical object deletion must go through the configured Django storage layer.

## Storage

Do not store image binaries in PostgreSQL.

The database stores the storage path/key and metadata.

Physical files live in Django storage.

Production direction:

```text
S3-compatible object storage
```

Do not hard-code local filesystem paths.

Google Drive is not primary production storage. It may only be used later as an import source if needed.

Production S3 configuration is a separate task.

## Not included yet

- video
- media type abstraction
- external URLs
- thumbnails
- width/height/file-size persistence
- provider-specific fields

---

# 13. Stock

Inventory for a concrete `ProductVariant`.

## Fields

| Field | Type / rule |
|---|---|
| `id` | PK |
| `variant_id` | FK -> `ProductVariant`, unique |
| `quantity` | non-negative integer, default `0` |
| `reserved` | non-negative integer, default `0` |
| `updated_at` | datetime |

## Constraints

```text
quantity >= 0
reserved >= 0
reserved <= quantity
```

One stock row per SKU:

```text
UNIQUE(variant_id)
```

Available quantity is derived:

```text
available = quantity - reserved
```

Do not persist an additional `is_in_stock` flag.

Deletion behavior:

```text
variant -> CASCADE
```

## Rules

`reserved` supports future checkout reservation semantics, but reservation behavior itself is not implemented at this stage.

Do not add warehouse entities until there is a real multi-warehouse requirement.

## Not included yet

- Warehouse
- inventory movement ledger
- stock history
- supplier stock
- reorder threshold
- backorders

---

# 14. ProductCompatibility

Directed product-to-product compatibility relation.

## Fields

| Field | Type / rule |
|---|---|
| `id` | PK |
| `product_id` | FK -> `Product` |
| `compatible_product_id` | FK -> `Product` |
| `created_at` | datetime |

## Constraints

```text
UNIQUE(product_id, compatible_product_id)
```

```text
product_id != compatible_product_id
```

## Example

```text
Silicone Case for iPhone 16
    -> compatible with
iPhone 16
```

The relation is intentionally directional.

From the reverse side, the application can query:

```text
Accessories compatible with iPhone 16
```

Do not model compatibility as comma-separated names or free-form strings.

Deletion behavior:

```text
product            -> CASCADE
compatible_product -> CASCADE
```

Normal lifecycle should usually archive products rather than physically delete them.

SKU-level compatibility is not implemented. Add it only if a real use case requires it.

---

# 15. Final relationship overview

```text
Category
   │
   ├── parent -> Category
   │
   ├── CategoryAttribute ───── Attribute ───── AttributeOption
   │
   └── ProductCategory ─────── Product
                                  │
Brand ────────────────────────────┤
                                  │
                                  ├── ProductAttributeValue ─── Attribute
                                  │
                                  ├── ProductMedia
                                  │
                                  ├── ProductCompatibility ──── Product
                                  │
                                  └── ProductVariant
                                         │
                                         ├── VariantAttributeValue ── Attribute
                                         ├── ProductMedia
                                         └── Stock
```

---

# 16. Main constraints summary

## Category

```text
slug UNIQUE
parent -> PROTECT
```

## Brand

```text
name UNIQUE
slug UNIQUE
```

## Product

```text
slug UNIQUE
brand -> PROTECT
status IN [draft, active, archived]
```

## ProductCategory

```text
UNIQUE(product, category)
UNIQUE(product) WHERE is_primary = true
category -> PROTECT
product -> CASCADE
```

## ProductVariant

```text
sku UNIQUE
barcode UNIQUE when present
price >= 0
compare_at_price IS NULL OR compare_at_price >= price
UNIQUE(product) WHERE is_default = true
product -> CASCADE
```

## Attribute

```text
slug UNIQUE
data_type IN [text, integer, decimal, boolean, option]
```

## AttributeOption

```text
UNIQUE(attribute, value)
```

## CategoryAttribute

```text
UNIQUE(category, attribute)
scope IN [product, variant]
```

## ProductAttributeValue

```text
UNIQUE(product, attribute)
exactly one typed value
```

## VariantAttributeValue

```text
UNIQUE(variant, attribute)
exactly one typed value
```

## ProductMedia

```text
variant.product == product when variant is present
one primary general image per product
one primary image per variant
```

## Stock

```text
variant UNIQUE
quantity >= 0
reserved >= 0
reserved <= quantity
```

## ProductCompatibility

```text
UNIQUE(product, compatible_product)
product != compatible_product
```

---

# 17. Important application-level invariants

The following rules are intentionally not forced by simple database constraints when they depend on another table or on publication workflow:

- `ProductMedia.variant.product_id == ProductMedia.product_id`
- typed attribute value field matches `Attribute.data_type`
- `AttributeOption.attribute_id == value.attribute_id`
- active/published products can later require at least one category
- active/published products can later require one default variant
- required `CategoryAttribute` values can be enforced before publication
- multiple category definitions for the same attribute must not conflict for one product

These rules should be implemented only when the corresponding admin/API/publication workflow is created.

---

# 18. Explicitly deferred domains

The following are not part of the current catalog-core implementation and require their own design stage:

- cart
- checkout
- registered-customer flows
- guest checkout
- orders
- order snapshots
- addresses
- payments
- shipments/delivery
- discounts/coupons
- multiple currencies
- multiple warehouses
- inventory movement ledger
- reviews/ratings
- SEO subsystem
- media processing pipeline
- production S3 configuration

Future cart/order items must reference `ProductVariant`.

Historical orders must store snapshots so later changes to products, prices, variants, or addresses do not mutate old order history.

Payment and shipment models must remain provider-neutral until real providers are selected.

---

# 19. Recommended implementation order

Implement the catalog schema in dependency order:

```text
1. Category + Brand

2. Product + ProductCategory + ProductVariant

3. Attribute + AttributeOption + CategoryAttribute

4. ProductAttributeValue + VariantAttributeValue

5. ProductMedia

6. Stock

7. ProductCompatibility
```

Before each implementation block:

1. compare the repository with this document;
2. do not recreate models/fields already present;
3. follow existing Django style;
4. create new migrations rather than editing applied migrations;
5. do not run `makemigrations` or `migrate` without explicit approval.

This document defines the approved target design; repository code and migrations define what has actually been implemented.
