import { Injectable, signal } from '@angular/core';

// @journeyos/shared/access-decision — NavigationService (Wave-0 stub).
// Deriva árvore de menu / breadcrumbs a partir das decisões de acesso.

export interface MenuNode {
  key: string;
  label: string;
  route: string;
  icon?: string;
  permission?: string;
  children?: MenuNode[];
}

export interface BreadcrumbItem {
  label: string;
  route?: string;
}

@Injectable({ providedIn: 'root' })
export class NavigationService {
  private readonly _menu = signal<MenuNode[]>([]);
  private readonly _breadcrumbs = signal<BreadcrumbItem[]>([]);

  readonly menu = this._menu.asReadonly();
  readonly breadcrumbs = this._breadcrumbs.asReadonly();

  /** Re-deriva o menu (ex.: na troca de empresa ou bump de modelo_acesso_versao). Stub. */
  setMenu(nodes: MenuNode[]): void {
    this._menu.set(nodes);
  }

  setBreadcrumbs(items: BreadcrumbItem[]): void {
    this._breadcrumbs.set(items);
  }
}
