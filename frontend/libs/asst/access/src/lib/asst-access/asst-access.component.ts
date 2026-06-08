import { ChangeDetectionStrategy, Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'jos-asst-access',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './asst-access.component.html',
  styleUrl: './asst-access.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AsstAccessComponent {}
