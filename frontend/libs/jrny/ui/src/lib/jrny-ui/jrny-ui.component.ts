import { ChangeDetectionStrategy, Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'jos-jrny-ui',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './jrny-ui.component.html',
  styleUrl: './jrny-ui.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class JrnyUiComponent {}
