import { ChangeDetectionStrategy, Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'jos-asst-feature-asset-studio',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './asst-feature-asset-studio.component.html',
  styleUrl: './asst-feature-asset-studio.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AsstFeatureAssetStudioComponent {}
