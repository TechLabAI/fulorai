import { ChangeDetectionStrategy, Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'jos-asst-feature-asset-library',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './asst-feature-asset-library.component.html',
  styleUrl: './asst-feature-asset-library.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AsstFeatureAssetLibraryComponent {}
