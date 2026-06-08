import { ChangeDetectionStrategy, Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'jos-sale-navigation',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './sale-navigation.component.html',
  styleUrl: './sale-navigation.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class SaleNavigationComponent {}
