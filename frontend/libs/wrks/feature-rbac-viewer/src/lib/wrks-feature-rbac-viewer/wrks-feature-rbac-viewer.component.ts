import { ChangeDetectionStrategy, Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'jos-wrks-feature-rbac-viewer',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './wrks-feature-rbac-viewer.component.html',
  styleUrl: './wrks-feature-rbac-viewer.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class WrksFeatureRbacViewerComponent {}
