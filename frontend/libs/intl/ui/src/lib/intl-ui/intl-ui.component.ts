import { ChangeDetectionStrategy, Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'jos-intl-ui',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './intl-ui.component.html',
  styleUrl: './intl-ui.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class IntlUiComponent {}
