import { ChangeDetectionStrategy, Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'jos-sale-access',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './sale-access.component.html',
  styleUrl: './sale-access.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class SaleAccessComponent {}
