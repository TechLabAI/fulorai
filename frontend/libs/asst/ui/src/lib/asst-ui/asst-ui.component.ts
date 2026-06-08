import { ChangeDetectionStrategy, Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'jos-asst-ui',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './asst-ui.component.html',
  styleUrl: './asst-ui.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AsstUiComponent {}
