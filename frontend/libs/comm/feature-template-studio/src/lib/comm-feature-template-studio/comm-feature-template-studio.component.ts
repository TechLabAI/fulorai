import { ChangeDetectionStrategy, Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'jos-comm-feature-template-studio',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './comm-feature-template-studio.component.html',
  styleUrl: './comm-feature-template-studio.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class CommFeatureTemplateStudioComponent {}
