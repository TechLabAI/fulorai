import { ChangeDetectionStrategy, Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'jos-asst-feature-approval-workflow',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './asst-feature-approval-workflow.component.html',
  styleUrl: './asst-feature-approval-workflow.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AsstFeatureApprovalWorkflowComponent {}
