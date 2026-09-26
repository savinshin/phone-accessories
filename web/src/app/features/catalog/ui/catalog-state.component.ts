import { ChangeDetectionStrategy, Component, input } from '@angular/core';

type CatalogStateKind = 'loading' | 'empty' | 'error';

@Component({
  selector: 'app-catalog-state',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    @if (kind() === 'error') {
      <p class="text-sm text-red-700" role="alert">{{ message() }}</p>
    } @else if (kind() === 'loading') {
      <p class="text-sm text-slate-600" role="status">{{ message() }}</p>
    } @else {
      <p class="text-sm text-slate-600" role="status">{{ message() }}</p>
    }
  `,
})
export class CatalogStateComponent {
  readonly kind = input.required<CatalogStateKind>();
  readonly message = input.required<string>();
}
