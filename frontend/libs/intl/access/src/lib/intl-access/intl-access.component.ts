import { ChangeDetectionStrategy, Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'jos-intl-access',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './intl-access.component.html',
  styleUrl: './intl-access.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class IntlAccessComponent {}
