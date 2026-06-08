import { ChangeDetectionStrategy, Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'jos-sale-styles',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './sale-styles.component.html',
  styleUrl: './sale-styles.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class SaleStylesComponent {}
