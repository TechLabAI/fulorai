import { ChangeDetectionStrategy, Component, signal } from '@angular/core';

@Component({
  selector: 'jos-ai-panel',
  standalone: true,
  imports: [],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <aside class="ai-panel" [class.collapsed]="!isOpen()">
      <button class="ai-panel-toggle" (click)="toggle()" type="button">
        @if (isOpen()) { ◀ IA } @else { ▶ }
      </button>
      @if (isOpen()) {
        <div class="ai-panel-content">
          <div class="ai-panel-header">IA Assistiva</div>
          <div class="ai-panel-body">
            <!-- Contextual insights injected by the active feature route via AiContextService -->
            <p class="ai-panel-placeholder">
              Selecione um item para ver análises e sugestões.
            </p>
          </div>
        </div>
      }
    </aside>
  `,
  styles: [`
    .ai-panel {
      display: flex;
      flex-direction: column;
      width: 320px;
      height: 100%;
      border-left: 1px solid #e5e7eb;
      transition: width 0.2s ease;
    }
    .ai-panel.collapsed { width: 32px; }
    .ai-panel-toggle { padding: 0.5rem; cursor: pointer; border: none; background: none; }
    .ai-panel-content { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
    .ai-panel-header { padding: 0.75rem 1rem; font-weight: 600; border-bottom: 1px solid #e5e7eb; }
    .ai-panel-body { flex: 1; overflow-y: auto; padding: 1rem; }
    .ai-panel-placeholder { color: #6b7280; font-size: 0.875rem; }
  `],
})
export class AiPanelComponent {
  readonly isOpen = signal(true);

  toggle(): void {
    this.isOpen.update(v => !v);
  }
}
