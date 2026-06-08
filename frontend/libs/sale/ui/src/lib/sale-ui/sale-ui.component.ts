import { ChangeDetectionStrategy, Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'jos-sale-ui',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './sale-ui.component.html',
  styleUrl: './sale-ui.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class SaleUiComponent {}
