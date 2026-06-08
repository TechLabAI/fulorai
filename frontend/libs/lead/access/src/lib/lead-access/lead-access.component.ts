import { ChangeDetectionStrategy, Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'jos-lead-access',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './lead-access.component.html',
  styleUrl: './lead-access.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class LeadAccessComponent {}
