import { ChangeDetectionStrategy, Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'jos-jrny-feature-routing-engine',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './jrny-feature-routing-engine.component.html',
  styleUrl: './jrny-feature-routing-engine.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class JrnyFeatureRoutingEngineComponent {}
