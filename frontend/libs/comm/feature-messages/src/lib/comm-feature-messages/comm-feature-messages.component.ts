import { ChangeDetectionStrategy, Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'jos-comm-feature-messages',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './comm-feature-messages.component.html',
  styleUrl: './comm-feature-messages.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class CommFeatureMessagesComponent {}
