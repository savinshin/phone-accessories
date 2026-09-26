import { ChangeDetectionStrategy, Component, DestroyRef, afterNextRender, inject, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { ActivatedRoute } from '@angular/router';
import { distinctUntilChanged, map } from 'rxjs';

import { CatalogApiService } from '../data-access/catalog-api.service';
import { Category } from '../data-access/catalog.types';
import { CatalogStateComponent } from '../ui/catalog-state.component';

@Component({
  selector: 'app-category-detail-page',
  imports: [CatalogStateComponent],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <main class="mx-auto max-w-3xl p-6">
      @if (isLoading()) {
        <app-catalog-state kind="loading" message="Loading category..." />
      } @else if (hasError()) {
        <app-catalog-state kind="error" message="Unable to load the category." />
      } @else if (category(); as category) {
        <h1 class="text-2xl font-semibold text-slate-900">{{ category.name }}</h1>
        @if (category.description) {
          <p class="mt-3 text-slate-600">{{ category.description }}</p>
        }
      }
    </main>
  `,
})
export class CategoryDetailPageComponent {
  private readonly route = inject(ActivatedRoute);
  private readonly catalogApi = inject(CatalogApiService);
  private readonly destroyRef = inject(DestroyRef);

  protected readonly category = signal<Category | null>(null);
  protected readonly isLoading = signal(true);
  protected readonly hasError = signal(false);

  constructor() {
    afterNextRender(() => {
      this.route.paramMap
        .pipe(
          map((params) => params.get('slug')!),
          distinctUntilChanged(),
          takeUntilDestroyed(this.destroyRef),
        )
        .subscribe((slug) => this.loadCategory(slug));
    });
  }

  private loadCategory(slug: string): void {
    this.category.set(null);
    this.hasError.set(false);
    this.isLoading.set(true);

    this.catalogApi
      .getCategory(slug)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (category) => {
          this.category.set(category);
          this.isLoading.set(false);
        },
        error: () => {
          this.hasError.set(true);
          this.isLoading.set(false);
        },
      });
  }
}
