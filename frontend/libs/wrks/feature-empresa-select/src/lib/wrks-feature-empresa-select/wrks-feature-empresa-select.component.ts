import { ChangeDetectionStrategy, Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'jos-wrks-feature-empresa-select',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './wrks-feature-empresa-select.component.html',
  styleUrl: './wrks-feature-empresa-select.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class WrksFeatureEmpresaSelectComponent {}
