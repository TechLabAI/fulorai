import { ChangeDetectionStrategy, Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'jos-comm-feature-routing-rules',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './comm-feature-routing-rules.component.html',
  styleUrl: './comm-feature-routing-rules.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class CommFeatureRoutingRulesComponent {}
