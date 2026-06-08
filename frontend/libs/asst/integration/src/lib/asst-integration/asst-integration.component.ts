import { ChangeDetectionStrategy, Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'jos-asst-integration',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './asst-integration.component.html',
  styleUrl: './asst-integration.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AsstIntegrationComponent {}
