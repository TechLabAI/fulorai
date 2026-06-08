import { ChangeDetectionStrategy, Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'jos-jrny-feature-journey-builder',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './jrny-feature-journey-builder.component.html',
  styleUrl: './jrny-feature-journey-builder.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class JrnyFeatureJourneyBuilderComponent {}
