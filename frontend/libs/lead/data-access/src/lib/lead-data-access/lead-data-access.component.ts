import { ChangeDetectionStrategy, Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'jos-lead-data-access',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './lead-data-access.component.html',
  styleUrl: './lead-data-access.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class LeadDataAccessComponent {}
