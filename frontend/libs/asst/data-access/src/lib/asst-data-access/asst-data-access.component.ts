import { ChangeDetectionStrategy, Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'jos-asst-data-access',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './asst-data-access.component.html',
  styleUrl: './asst-data-access.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AsstDataAccessComponent {}
