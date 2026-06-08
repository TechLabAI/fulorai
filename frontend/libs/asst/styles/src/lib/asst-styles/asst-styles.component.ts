import { ChangeDetectionStrategy, Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'jos-asst-styles',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './asst-styles.component.html',
  styleUrl: './asst-styles.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AsstStylesComponent {}
