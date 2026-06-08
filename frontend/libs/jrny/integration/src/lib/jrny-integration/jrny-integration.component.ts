import { ChangeDetectionStrategy, Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'jos-jrny-integration',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './jrny-integration.component.html',
  styleUrl: './jrny-integration.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class JrnyIntegrationComponent {}
