import { ChangeDetectionStrategy, Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'jos-jrny-data-access',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './jrny-data-access.component.html',
  styleUrl: './jrny-data-access.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class JrnyDataAccessComponent {}
