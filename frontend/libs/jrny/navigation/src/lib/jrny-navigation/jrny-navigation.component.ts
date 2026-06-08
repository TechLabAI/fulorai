import { ChangeDetectionStrategy, Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'jos-jrny-navigation',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './jrny-navigation.component.html',
  styleUrl: './jrny-navigation.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class JrnyNavigationComponent {}
