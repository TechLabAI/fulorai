import { ChangeDetectionStrategy, Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'jos-lead-feature-qualification-rules',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './lead-feature-qualification-rules.component.html',
  styleUrl: './lead-feature-qualification-rules.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class LeadFeatureQualificationRulesComponent {}
