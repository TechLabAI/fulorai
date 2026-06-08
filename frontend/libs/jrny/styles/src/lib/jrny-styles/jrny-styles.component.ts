import { ChangeDetectionStrategy, Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'jos-jrny-styles',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './jrny-styles.component.html',
  styleUrl: './jrny-styles.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class JrnyStylesComponent {}
