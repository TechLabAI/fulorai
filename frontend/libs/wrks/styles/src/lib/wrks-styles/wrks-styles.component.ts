import { ChangeDetectionStrategy, Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'jos-wrks-styles',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './wrks-styles.component.html',
  styleUrl: './wrks-styles.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class WrksStylesComponent {}
