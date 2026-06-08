import { ChangeDetectionStrategy, Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'jos-lead-feature-lead-list',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './lead-feature-lead-list.component.html',
  styleUrl: './lead-feature-lead-list.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class LeadFeatureLeadListComponent {}
