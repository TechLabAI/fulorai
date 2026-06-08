import { ChangeDetectionStrategy, Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'jos-comm-feature-channel-config',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './comm-feature-channel-config.component.html',
  styleUrl: './comm-feature-channel-config.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class CommFeatureChannelConfigComponent {}
