import { ChangeDetectionStrategy, Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'jos-intl-integration',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './intl-integration.component.html',
  styleUrl: './intl-integration.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class IntlIntegrationComponent {}
