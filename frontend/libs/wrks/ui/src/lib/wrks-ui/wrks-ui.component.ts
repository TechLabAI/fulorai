import { ChangeDetectionStrategy, Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'jos-wrks-ui',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './wrks-ui.component.html',
  styleUrl: './wrks-ui.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class WrksUiComponent {}
