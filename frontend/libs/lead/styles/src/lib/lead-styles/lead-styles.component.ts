import { ChangeDetectionStrategy, Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'jos-lead-styles',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './lead-styles.component.html',
  styleUrl: './lead-styles.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class LeadStylesComponent {}
