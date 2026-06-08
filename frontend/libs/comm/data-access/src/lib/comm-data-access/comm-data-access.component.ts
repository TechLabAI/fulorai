import { ChangeDetectionStrategy, Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'jos-comm-data-access',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './comm-data-access.component.html',
  styleUrl: './comm-data-access.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class CommDataAccessComponent {}
