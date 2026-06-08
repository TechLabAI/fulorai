import { ChangeDetectionStrategy, Component, input } from '@angular/core';

// @journeyos/shared/ui-feedback — Wave-0 API surface (stub).
// Estados padrão empty/loading/error. Standalone + OnPush.

@Component({
  selector: 'jos-loading',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `<div class="jos-loading" role="status" aria-live="polite">Carregando…</div>`,
})
export class JosLoadingComponent {}

@Component({
  selector: 'jos-empty-state',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `<div class="jos-empty"><p>{{ message() }}</p></div>`,
})
export class JosEmptyStateComponent {
  readonly message = input<string>('Nada por aqui');
}

@Component({
  selector: 'jos-error',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `<div class="jos-error" role="alert"><p>{{ message() }}</p></div>`,
})
export class JosErrorComponent {
  readonly message = input<string>('Algo deu errado');
}
