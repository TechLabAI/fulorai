import { ChangeDetectionStrategy, Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'jos-asst-navigation',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './asst-navigation.component.html',
  styleUrl: './asst-navigation.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AsstNavigationComponent {}
