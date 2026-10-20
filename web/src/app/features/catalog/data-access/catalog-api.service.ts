import { HttpClient, HttpParams } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { Brand, Category, ProductDetail, ProductListItem } from './catalog.types';

@Injectable({ providedIn: 'root' })
export class CatalogApiService {
  private readonly http = inject(HttpClient);

  getCategories(): Observable<Category[]> {
    return this.http.get<Category[]>('/api/catalog/categories/');
  }

  getCategory(slug: string): Observable<Category> {
    return this.http.get<Category>('/api/catalog/categories/' + slug + '/');
  }

  getBrands(): Observable<Brand[]> {
    return this.http.get<Brand[]>('/api/catalog/brands/');
  }

  getBrand(slug: string): Observable<Brand> {
    return this.http.get<Brand>('/api/catalog/brands/' + slug + '/');
  }

  getProducts(category: string | null, brand: string | null): Observable<ProductListItem[]> {
    let params = new HttpParams();

    if (category) {
      params = params.set('category', category);
    }

    if (brand) {
      params = params.set('brand', brand);
    }

    return this.http.get<ProductListItem[]>('/api/catalog/products/', { params });
  }

  getProduct(slug: string): Observable<ProductDetail> {
    return this.http.get<ProductDetail>('/api/catalog/products/' + slug + '/');
  }
}
