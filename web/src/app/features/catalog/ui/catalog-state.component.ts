import { ChangeDetectionStrategy, Component, input } from '@angular/core';

type CatalogStateKind = 'loading' | 'empty' | 'error';

@Component({
  selector: 'app-catalog-state',
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './catalog-state.component.html',
})
export class CatalogStateComponent {
  readonly kind = input.required<CatalogStateKind>();
  readonly message = input.required<string>();
}
