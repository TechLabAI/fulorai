import { ChangeDetectionStrategy, Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'jos-lead-feature-survey',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './lead-feature-survey.component.html',
  styleUrl: './lead-feature-survey.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class LeadFeatureSurveyComponent {}
