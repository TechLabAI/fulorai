import { ChangeDetectionStrategy, Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'jos-wrks-feature-login',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './wrks-feature-login.component.html',
  styleUrl: './wrks-feature-login.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class WrksFeatureLoginComponent {}
