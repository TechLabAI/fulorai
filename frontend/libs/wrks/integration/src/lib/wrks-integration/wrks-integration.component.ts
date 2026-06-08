import { ChangeDetectionStrategy, Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'jos-wrks-integration',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './wrks-integration.component.html',
  styleUrl: './wrks-integration.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class WrksIntegrationComponent {}
