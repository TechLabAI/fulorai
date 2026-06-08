import { ChangeDetectionStrategy, Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'jos-comm-ui',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './comm-ui.component.html',
  styleUrl: './comm-ui.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class CommUiComponent {}
