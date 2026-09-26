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
