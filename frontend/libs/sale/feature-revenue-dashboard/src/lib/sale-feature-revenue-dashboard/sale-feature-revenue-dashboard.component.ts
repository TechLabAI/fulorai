import { ChangeDetectionStrategy, Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'jos-sale-feature-revenue-dashboard',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './sale-feature-revenue-dashboard.component.html',
  styleUrl: './sale-feature-revenue-dashboard.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class SaleFeatureRevenueDashboardComponent {}
