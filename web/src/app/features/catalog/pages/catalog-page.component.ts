import { ChangeDetectionStrategy, Component, DestroyRef, afterNextRender, computed, inject, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { RouterLink } from '@angular/router';
import { forkJoin } from 'rxjs';

import { CatalogApiService } from '../data-access/catalog-api.service';
import { Brand, Category } from '../data-access/catalog.types';
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

  protected readonly categories = signal<Category[]>([]);
  protected readonly brands = signal<Brand[]>([]);
  protected readonly isLoading = signal(true);
  protected readonly hasError = signal(false);
  protected readonly isEmpty = computed(
    () => !this.isLoading() && !this.hasError() && !this.categories().length && !this.brands().length,
  );

  constructor() {
    afterNextRender(() => this.loadCatalog());
  }

  private loadCatalog(): void {
    forkJoin({
      categories: this.catalogApi.getCategories(),
      brands: this.catalogApi.getBrands(),
    })
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: ({ categories, brands }) => {
          this.categories.set(categories);
          this.brands.set(brands);
          this.isLoading.set(false);
        },
        error: () => {
          this.hasError.set(true);
          this.isLoading.set(false);
        },
      });
  }
}
