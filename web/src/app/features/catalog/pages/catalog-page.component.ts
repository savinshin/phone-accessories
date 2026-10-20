import { ChangeDetectionStrategy, Component, DestroyRef, afterNextRender, computed, inject, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { catchError, distinctUntilChanged, EMPTY, forkJoin, map, switchMap } from 'rxjs';

import { CatalogApiService } from '../data-access/catalog-api.service';
import { Brand, Category, ProductListItem } from '../data-access/catalog.types';
import { CatalogStateComponent } from '../ui/catalog-state.component';

@Component({
  selector: 'app-catalog-page',
  imports: [RouterLink, CatalogStateComponent],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './catalog-page.component.html',
})
export class CatalogPageComponent {
  private readonly catalogApi = inject(CatalogApiService);
  private readonly destroyRef = inject(DestroyRef);
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);

  protected readonly categories = signal<Category[]>([]);
  protected readonly brands = signal<Brand[]>([]);
  protected readonly navigationIsLoading = signal(true);
  protected readonly navigationHasError = signal(false);
  protected readonly navigationIsEmpty = computed(
    () =>
      !this.navigationIsLoading() &&
      !this.navigationHasError() &&
      !this.categories().length &&
      !this.brands().length,
  );
  protected readonly products = signal<ProductListItem[]>([]);
  protected readonly productsIsLoading = signal(true);
  protected readonly productsHasError = signal(false);
  protected readonly productsIsEmpty = computed(
    () => !this.productsIsLoading() && !this.productsHasError() && !this.products().length,
  );
  protected readonly selectedCategory = signal('');
  protected readonly selectedBrand = signal('');

  constructor() {
    afterNextRender(() => {
      this.loadNavigation();
      this.loadProducts();
    });
  }

  protected updateCategoryFilter(category: string): void {
    this.router.navigate([], {
      relativeTo: this.route,
      queryParams: { category: category || null },
      queryParamsHandling: 'merge',
    });
  }

  protected updateBrandFilter(brand: string): void {
    this.router.navigate([], {
      relativeTo: this.route,
      queryParams: { brand: brand || null },
      queryParamsHandling: 'merge',
    });
  }

  private loadNavigation(): void {
    forkJoin({
      categories: this.catalogApi.getCategories(),
      brands: this.catalogApi.getBrands(),
    })
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: ({ categories, brands }) => {
          this.categories.set(categories);
          this.brands.set(brands);
          this.navigationIsLoading.set(false);
        },
        error: () => {
          this.navigationHasError.set(true);
          this.navigationIsLoading.set(false);
        },
      });
  }

  private loadProducts(): void {
    this.route.queryParamMap
      .pipe(
        map((params) => ({
          category: params.get('category'),
          brand: params.get('brand'),
        })),
        distinctUntilChanged(
          (previous, current) => previous.category === current.category && previous.brand === current.brand,
        ),
        switchMap(({ category, brand }) => {
          this.selectedCategory.set(category ?? '');
          this.selectedBrand.set(brand ?? '');
          this.products.set([]);
          this.productsHasError.set(false);
          this.productsIsLoading.set(true);

          return this.catalogApi.getProducts(category, brand).pipe(
            catchError(() => {
              this.productsHasError.set(true);
              this.productsIsLoading.set(false);
              return EMPTY;
            }),
          );
        }),
        takeUntilDestroyed(this.destroyRef),
      )
      .subscribe((products) => {
        this.products.set(products);
        this.productsIsLoading.set(false);
      });
  }
}
