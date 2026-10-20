import { ChangeDetectionStrategy, Component, DestroyRef, inject, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { ActivatedRoute } from '@angular/router';
import { catchError, distinctUntilChanged, EMPTY, map, switchMap } from 'rxjs';

import { CatalogApiService } from '../data-access/catalog-api.service';
import { ProductDetail, ProductVariant } from '../data-access/catalog.types';
import { CatalogStateComponent } from '../ui/catalog-state.component';

@Component({
  selector: 'app-product-detail-page',
  imports: [CatalogStateComponent],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './product-detail-page.component.html',
})
export class ProductDetailPageComponent {
  private readonly catalogApi = inject(CatalogApiService);
  private readonly destroyRef = inject(DestroyRef);
  private readonly route = inject(ActivatedRoute);

  protected readonly product = signal<ProductDetail | null>(null);
  protected readonly selectedVariant = signal<ProductVariant | null>(null);
  protected readonly isLoading = signal(true);
  protected readonly hasError = signal(false);

  constructor() {
    this.route.paramMap
      .pipe(
        map((params) => params.get('slug')!),
        distinctUntilChanged(),
        switchMap((slug) => {
          this.product.set(null);
          this.selectedVariant.set(null);
          this.hasError.set(false);
          this.isLoading.set(true);

          return this.catalogApi.getProduct(slug).pipe(
            catchError(() => {
              this.hasError.set(true);
              this.isLoading.set(false);
              return EMPTY;
            }),
          );
        }),
        takeUntilDestroyed(this.destroyRef),
      )
      .subscribe((product) => {
        this.product.set(product);
        this.selectedVariant.set(product.variants.find((variant) => variant.is_default) ?? null);
        this.isLoading.set(false);
      });
  }

  protected selectVariant(variant: ProductVariant): void {
    this.selectedVariant.set(variant);
  }
}
