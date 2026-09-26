import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { Brand, Category } from './catalog.types';

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
}
