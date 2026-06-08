import { ChangeDetectionStrategy, Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'jos-wrks-feature-users',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './wrks-feature-users.component.html',
  styleUrl: './wrks-feature-users.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class WrksFeatureUsersComponent {}
