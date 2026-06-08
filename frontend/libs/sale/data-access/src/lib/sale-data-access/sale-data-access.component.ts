import { ChangeDetectionStrategy, Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'jos-sale-data-access',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './sale-data-access.component.html',
  styleUrl: './sale-data-access.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class SaleDataAccessComponent {}
