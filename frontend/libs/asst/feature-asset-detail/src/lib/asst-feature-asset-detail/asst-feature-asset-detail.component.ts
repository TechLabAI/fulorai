import { ChangeDetectionStrategy, Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'jos-asst-feature-asset-detail',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './asst-feature-asset-detail.component.html',
  styleUrl: './asst-feature-asset-detail.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AsstFeatureAssetDetailComponent {}
