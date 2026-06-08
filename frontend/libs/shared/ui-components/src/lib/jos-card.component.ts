import { ChangeDetectionStrategy, Component, input } from '@angular/core';

// @journeyos/shared/ui-components — Wave-0 API surface (stub).
// Componentes base (Material-wrapped) + primitivos de layout. Standalone + OnPush.

@Component({
  selector: 'jos-card',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `<section class="jos-card">@if (title()) {<h3>{{ title() }}</h3>}<ng-content /></section>`,
})
export class JosCardComponent {
  readonly title = input<string>('');
}
