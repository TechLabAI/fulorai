import { ChangeDetectionStrategy, Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'jos-wrks-data-access',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './wrks-data-access.component.html',
  styleUrl: './wrks-data-access.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class WrksDataAccessComponent {}
