import { ChangeDetectionStrategy, Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'jos-comm-navigation',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './comm-navigation.component.html',
  styleUrl: './comm-navigation.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class CommNavigationComponent {}
