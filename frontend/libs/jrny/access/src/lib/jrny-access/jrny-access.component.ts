import { ChangeDetectionStrategy, Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'jos-jrny-access',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './jrny-access.component.html',
  styleUrl: './jrny-access.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class JrnyAccessComponent {}
