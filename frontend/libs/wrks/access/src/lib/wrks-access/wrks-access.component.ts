import { ChangeDetectionStrategy, Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'jos-wrks-access',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './wrks-access.component.html',
  styleUrl: './wrks-access.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class WrksAccessComponent {}
