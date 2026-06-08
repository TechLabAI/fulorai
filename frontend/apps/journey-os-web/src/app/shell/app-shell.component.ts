import { ChangeDetectionStrategy, Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { SidebarComponent } from './sidebar.component';
import { TopbarComponent } from './topbar.component';
import { AiPanelComponent } from './ai-panel.component';

@Component({
  selector: 'jos-shell',
  standalone: true,
  imports: [
    RouterOutlet,
    SidebarComponent,
    TopbarComponent,
    AiPanelComponent,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="shell-layout">
      <jos-sidebar class="shell-sidebar" />
      <div class="shell-main">
        <jos-topbar class="shell-topbar" />
        <main class="shell-content">
          <router-outlet />
        </main>
      </div>
      <jos-ai-panel class="shell-ai-panel" />
    </div>
  `,
  styles: [`
    .shell-layout {
      display: grid;
      grid-template-columns: auto 1fr auto;
      grid-template-rows: 1fr;
      height: 100vh;
      overflow: hidden;
    }
    .shell-main {
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }
    .shell-content {
      flex: 1;
      overflow: auto;
    }
  `],
})
export class AppShellComponent {}
