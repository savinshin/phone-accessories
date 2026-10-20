export interface Category {
  id: number;
  parent_id: number | null;
  name: string;
  slug: string;
  description: string;
  sort_order: number;
}

export interface Brand {
  id: number;
  name: string;
  slug: string;
  description: string;
}

export interface BrandShort {
  id: number;
  name: string;
  slug: string;
}

export interface ProductVariantShort {
  id: number;
  sku: string;
  price: string;
  compare_at_price: string | null;
}

export interface ProductVariant {
  id: number;
  sku: string;
  barcode: string | null;
  price: string;
  compare_at_price: string | null;
  is_default: boolean;
  sort_order: number;
}

export interface ProductCategory {
  id: number;
  name: string;
  slug: string;
  is_primary: boolean;
}

export interface ProductListItem {
  id: number;
  name: string;
  slug: string;
  brand: BrandShort | null;
  default_variant: ProductVariantShort | null;
}

export interface ProductDetail {
  id: number;
  name: string;
  slug: string;
  description: string;
  brand: BrandShort | null;
  default_variant: ProductVariantShort | null;
  categories: ProductCategory[];
  variants: ProductVariant[];
}
