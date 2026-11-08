# Phone Accessories

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

People shopping for electronics and accessories who want to find, compare, and choose products conveniently from a computer or phone.

## Product Purpose

Build a complete online store suitable for a professional portfolio and subsequent commercial use or transfer to a client. Success means a usable shopping experience grounded in actual product data, with production-quality implementation and presentation.

## Positioning

Phone Accessories is a working name. The final brand and distinguishing commercial advantages have not been defined. Do not invent a market position or business claims.

## Operating Context

- The storefront must work on desktop, tablet, and mobile browsers.
- Local development uses Docker Compose with Angular, Django REST Framework, and PostgreSQL. Internal catalog management uses Django Admin.
- The current development catalog has reproducible ORM demo data from `backend/catalog/management/commands/seed_catalog.py`. Demo products are development evidence, not claims about a real retailer's inventory.

## Capabilities and Constraints

- The current storefront supports Category and Brand navigation, Product listings, Category/Brand URL filters, Product details, and selection of a ProductVariant by SKU.
- `Product` represents a product model; `ProductVariant` represents a sellable SKU and owns its price. A product can have no brand or no default variant. Those are valid states, not reasons to invent fallback data.
- The user's goal includes comparing products; a dedicated product-comparison feature is not currently implemented.
- Angular 22 and Tailwind CSS 4 are the existing frontend stack, with standalone components, OnPush, separate TypeScript/HTML, and SSR/hydration. API requests use relative `/api/...` paths.
- Functional work and design work are separate passes. A design pass preserves API contracts, routes, query behavior, state, TypeScript application logic, and SSR/hydration. `AGENTS.md` remains the authority for implementation and command restrictions.
- UI libraries, dependencies, design systems, and custom design tokens require a separate project decision.
- Product media, stock, attributes, compatibility, cart, checkout, and payments are future capabilities. Do not present them as available before their dedicated implementation.
- Prices come from the API. The API does not provide a currency; do not add one or invent availability, specifications, images, or commercial promises.

## Brand Commitments

- The target market and final interface language are undecided. The current English interface is temporary.
- Final branding and unique selling points remain open decisions.
- Use factual, clear interface copy. Do not invent delivery terms, discounts, guarantees, customer testimonials, or retailer advantages.

## Evidence on Hand

- `AGENTS.md` records the project's purpose, architecture, frontend workflow, and boundaries.
- `web/src/app/features/catalog/` contains the working storefront implementation and frontend API types.
- `backend/catalog/models.py` and `backend/catalog/serializers.py` define the actual domain and response contracts.
- `seed_catalog.py` defines eight Categories, eight Brands, six demo Products, six primary ProductCategory relations, and eight active ProductVariants. It includes a product without a brand and a product without a default variant.
- Product imagery and confirmed commercial proof have not been supplied for the current catalog work.

## Product Principles

- Make products the main content of the catalog; keep navigation and filters easy to reach without displacing the product list.
- Show only information supported by the real API and confirmed product facts.
- Make finding and choosing a product understandable across desktop and mobile.
- Preserve working functionality while improving presentation, and add future capabilities only in their own agreed tasks.

## Accessibility & Inclusion

Preserve semantic HTML, labelled native controls, keyboard operation, visible focus, readable contrast, responsive layouts, and the existing loading/error/empty semantics. No additional audience-specific accessibility requirements or formal compliance target have been established.

## Open Decisions

- Target market and locale.
- Final interface language and currency.
- Final store name, brand identity, and commercial differentiation.
