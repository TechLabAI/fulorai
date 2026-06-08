import { ChangeDetectionStrategy, Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'jos-lead-navigation',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './lead-navigation.component.html',
  styleUrl: './lead-navigation.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class LeadNavigationComponent {}
