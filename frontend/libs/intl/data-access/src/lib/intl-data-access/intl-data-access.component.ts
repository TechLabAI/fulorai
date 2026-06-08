import { ChangeDetectionStrategy, Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'jos-intl-data-access',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './intl-data-access.component.html',
  styleUrl: './intl-data-access.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class IntlDataAccessComponent {}
