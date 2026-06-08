import { ChangeDetectionStrategy, Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'jos-intl-feature-analytics',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './intl-feature-analytics.component.html',
  styleUrl: './intl-feature-analytics.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class IntlFeatureAnalyticsComponent {}
