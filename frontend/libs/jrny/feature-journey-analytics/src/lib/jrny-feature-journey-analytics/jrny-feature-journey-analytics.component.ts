import { ChangeDetectionStrategy, Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'jos-jrny-feature-journey-analytics',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './jrny-feature-journey-analytics.component.html',
  styleUrl: './jrny-feature-journey-analytics.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class JrnyFeatureJourneyAnalyticsComponent {}
