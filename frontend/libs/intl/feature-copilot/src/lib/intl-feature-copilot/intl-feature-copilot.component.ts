import { ChangeDetectionStrategy, Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'jos-intl-feature-copilot',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './intl-feature-copilot.component.html',
  styleUrl: './intl-feature-copilot.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class IntlFeatureCopilotComponent {}
