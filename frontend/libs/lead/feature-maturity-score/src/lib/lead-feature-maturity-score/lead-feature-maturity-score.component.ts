import { ChangeDetectionStrategy, Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'jos-lead-feature-maturity-score',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './lead-feature-maturity-score.component.html',
  styleUrl: './lead-feature-maturity-score.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class LeadFeatureMaturityScoreComponent {}
