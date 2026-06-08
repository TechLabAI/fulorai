import { ChangeDetectionStrategy, Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'jos-sale-feature-attribution',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './sale-feature-attribution.component.html',
  styleUrl: './sale-feature-attribution.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class SaleFeatureAttributionComponent {}
