import { ChangeDetectionStrategy, Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'jos-wrks-navigation',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './wrks-navigation.component.html',
  styleUrl: './wrks-navigation.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class WrksNavigationComponent {}
