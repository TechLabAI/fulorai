import { ChangeDetectionStrategy, Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'jos-intl-styles',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './intl-styles.component.html',
  styleUrl: './intl-styles.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class IntlStylesComponent {}
