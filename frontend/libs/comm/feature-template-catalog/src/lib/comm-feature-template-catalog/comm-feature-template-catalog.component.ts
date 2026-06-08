import { ChangeDetectionStrategy, Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'jos-comm-feature-template-catalog',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './comm-feature-template-catalog.component.html',
  styleUrl: './comm-feature-template-catalog.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class CommFeatureTemplateCatalogComponent {}
