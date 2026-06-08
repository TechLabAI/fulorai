import { ChangeDetectionStrategy, Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'jos-intl-feature-knowledge',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './intl-feature-knowledge.component.html',
  styleUrl: './intl-feature-knowledge.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class IntlFeatureKnowledgeComponent {}
