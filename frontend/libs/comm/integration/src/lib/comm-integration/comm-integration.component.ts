import { ChangeDetectionStrategy, Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'jos-comm-integration',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './comm-integration.component.html',
  styleUrl: './comm-integration.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class CommIntegrationComponent {}
