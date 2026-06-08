import { ChangeDetectionStrategy, Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'jos-comm-styles',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './comm-styles.component.html',
  styleUrl: './comm-styles.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class CommStylesComponent {}
