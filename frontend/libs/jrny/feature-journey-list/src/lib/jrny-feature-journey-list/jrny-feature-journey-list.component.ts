import { ChangeDetectionStrategy, Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'jos-jrny-feature-journey-list',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './jrny-feature-journey-list.component.html',
  styleUrl: './jrny-feature-journey-list.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class JrnyFeatureJourneyListComponent {}
