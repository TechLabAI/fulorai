import { Injectable, signal } from '@angular/core';

// @journeyos/shared/access-decision — Wave-0 API surface (stub).
// Avalia permissões/feature-flags. A UI NUNCA decide RBAC localmente — sempre via can().

export interface AccessDecision {
  papel: string;
  permissoes: string[];
  dataScope?: string;
  modeloAcessoVersao: number;
}

@Injectable({ providedIn: 'root' })
export class AccessDecisionService {
  private readonly _decision = signal<AccessDecision | null>(null);
  readonly decision = this._decision.asReadonly();

  setDecision(d: AccessDecision | null): void {
    this._decision.set(d);
  }

  /** true se o usuário tem a permissão `<modulo>.<recurso>.<acao>`. Stub. */
  can(permission: string): boolean {
    return this._decision()?.permissoes.includes(permission) ?? false;
  }
}

@Injectable({ providedIn: 'root' })
export class PermissionService {
  /** Reexpõe avaliação de permissão para componentes que preferem este nome. */
  constructor(private readonly access: AccessDecisionService) {}
  can(permission: string): boolean {
    return this.access.can(permission);
  }
}
