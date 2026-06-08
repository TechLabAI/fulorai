import { ChangeDetectionStrategy, Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'jos-lead-feature-lead-detail',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './lead-feature-lead-detail.component.html',
  styleUrl: './lead-feature-lead-detail.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class LeadFeatureLeadDetailComponent {}
