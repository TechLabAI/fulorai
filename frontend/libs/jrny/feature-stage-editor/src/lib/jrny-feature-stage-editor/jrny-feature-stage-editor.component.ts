import { ChangeDetectionStrategy, Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'jos-jrny-feature-stage-editor',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './jrny-feature-stage-editor.component.html',
  styleUrl: './jrny-feature-stage-editor.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class JrnyFeatureStageEditorComponent {}
