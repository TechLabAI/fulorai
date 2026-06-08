import { ChangeDetectionStrategy, Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'jos-comm-access',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './comm-access.component.html',
  styleUrl: './comm-access.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class CommAccessComponent {}
