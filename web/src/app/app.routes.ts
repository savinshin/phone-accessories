import { Routes } from '@angular/router';

export const routes: Routes = [
  {
    path: 'catalog',
    loadComponent: () =>
      import('./features/catalog/pages/catalog-page.component').then(
        (component) => component.CatalogPageComponent,
      ),
  },
  {
    path: 'catalog/categories/:slug',
    loadComponent: () =>
      import('./features/catalog/pages/category-detail-page.component').then(
        (component) => component.CategoryDetailPageComponent,
      ),
  },
  {
    path: 'catalog/brands/:slug',
    loadComponent: () =>
      import('./features/catalog/pages/brand-detail-page.component').then(
        (component) => component.BrandDetailPageComponent,
      ),
  },
  {
    path: 'catalog/products/:slug',
    loadComponent: () =>
      import('./features/catalog/pages/product-detail-page.component').then(
        (component) => component.ProductDetailPageComponent,
      ),
  },
];
