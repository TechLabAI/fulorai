import { ChangeDetectionStrategy, Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'jos-sale-integration',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './sale-integration.component.html',
  styleUrl: './sale-integration.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class SaleIntegrationComponent {}
