import { ChangeDetectionStrategy, Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'jos-sale-feature-offer',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './sale-feature-offer.component.html',
  styleUrl: './sale-feature-offer.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class SaleFeatureOfferComponent {}
