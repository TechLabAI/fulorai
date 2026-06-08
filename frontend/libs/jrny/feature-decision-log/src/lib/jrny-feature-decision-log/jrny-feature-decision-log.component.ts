import { ChangeDetectionStrategy, Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'jos-jrny-feature-decision-log',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './jrny-feature-decision-log.component.html',
  styleUrl: './jrny-feature-decision-log.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class JrnyFeatureDecisionLogComponent {}
