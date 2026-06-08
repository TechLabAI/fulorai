import { ChangeDetectionStrategy, Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'jos-lead-feature-segmentation',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './lead-feature-segmentation.component.html',
  styleUrl: './lead-feature-segmentation.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class LeadFeatureSegmentationComponent {}
