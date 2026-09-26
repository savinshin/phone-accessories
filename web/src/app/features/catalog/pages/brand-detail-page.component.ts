import { ChangeDetectionStrategy, Component, DestroyRef, afterNextRender, inject, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { ActivatedRoute } from '@angular/router';
import { catchError, distinctUntilChanged, EMPTY, map, switchMap } from 'rxjs';

import { CatalogApiService } from '../data-access/catalog-api.service';
import { Brand } from '../data-access/catalog.types';
import { CatalogStateComponent } from '../ui/catalog-state.component';

@Component({
  selector: 'app-brand-detail-page',
  imports: [CatalogStateComponent],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <main class="mx-auto max-w-3xl p-6">
      @if (isLoading()) {
        <app-catalog-state kind="loading" message="Loading brand..." />
      } @else if (hasError()) {
        <app-catalog-state kind="error" message="Unable to load the brand." />
      } @else if (brand(); as brand) {
        <h1 class="text-2xl font-semibold text-slate-900">{{ brand.name }}</h1>
        @if (brand.description) {
          <p class="mt-3 text-slate-600">{{ brand.description }}</p>
        }
      }
    </main>
  `,
})
export class BrandDetailPageComponent {
  private readonly route = inject(ActivatedRoute);
  private readonly catalogApi = inject(CatalogApiService);
  private readonly destroyRef = inject(DestroyRef);

  protected readonly brand = signal<Brand | null>(null);
  protected readonly isLoading = signal(true);
  protected readonly hasError = signal(false);

  constructor() {
    afterNextRender(() => {
      this.route.paramMap
        .pipe(
          map((params) => params.get('slug')!),
          distinctUntilChanged(),
          switchMap((slug) => {
            this.brand.set(null);
            this.hasError.set(false);
            this.isLoading.set(true);

            return this.catalogApi.getBrand(slug).pipe(
              catchError(() => {
                this.hasError.set(true);
                this.isLoading.set(false);

                return EMPTY;
              }),
            );
          }),
          takeUntilDestroyed(this.destroyRef),
        )
        .subscribe((brand) => {
          this.brand.set(brand);
          this.isLoading.set(false);
        });
    });
  }
}
