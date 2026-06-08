import { ChangeDetectionStrategy, Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'jos-sale-feature-pipeline',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './sale-feature-pipeline.component.html',
  styleUrl: './sale-feature-pipeline.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class SaleFeaturePipelineComponent {}
