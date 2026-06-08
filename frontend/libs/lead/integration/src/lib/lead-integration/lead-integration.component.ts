import { ChangeDetectionStrategy, Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'jos-lead-integration',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './lead-integration.component.html',
  styleUrl: './lead-integration.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class LeadIntegrationComponent {}
