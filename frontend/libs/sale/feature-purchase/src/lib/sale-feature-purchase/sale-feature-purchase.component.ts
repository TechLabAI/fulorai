import { ChangeDetectionStrategy, Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'jos-sale-feature-purchase',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './sale-feature-purchase.component.html',
  styleUrl: './sale-feature-purchase.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class SaleFeaturePurchaseComponent {}
