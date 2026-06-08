import { ChangeDetectionStrategy, Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'jos-intl-navigation',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './intl-navigation.component.html',
  styleUrl: './intl-navigation.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class IntlNavigationComponent {}
