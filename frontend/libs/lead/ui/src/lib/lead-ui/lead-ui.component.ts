import { ChangeDetectionStrategy, Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'jos-lead-ui',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './lead-ui.component.html',
  styleUrl: './lead-ui.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class LeadUiComponent {}
