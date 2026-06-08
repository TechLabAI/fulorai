import { ChangeDetectionStrategy, Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'jos-sale-feature-opportunity',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './sale-feature-opportunity.component.html',
  styleUrl: './sale-feature-opportunity.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class SaleFeatureOpportunityComponent {}
