import { ChangeDetectionStrategy, Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'jos-wrks-feature-workspace',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './wrks-feature-workspace.component.html',
  styleUrl: './wrks-feature-workspace.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class WrksFeatureWorkspaceComponent {}
