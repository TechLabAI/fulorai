import { Injectable, signal } from '@angular/core';

// @journeyos/shared/auth-session — Wave-0 API surface (stub).
// Única fonte da sessão (JWT/claims). Login/logout/refresh/restore via OIDC contra o wrks-service.
// NUNCA ler localStorage/sessionStorage direto fora desta lib (access-layer-contracts §checks).

export type SessionStatus =
  | 'anonymous'
  | 'authenticating'
  | 'authenticated'
  | 'error';

export interface SessionClaims {
  userId: string;
  nome: string;
  email: string;
  empresaId?: string;
  mfaRequired?: boolean;
}

@Injectable({ providedIn: 'root' })
export class AuthSessionService {
  private readonly _status = signal<SessionStatus>('anonymous');
  private readonly _claims = signal<SessionClaims | null>(null);

  readonly status = this._status.asReadonly();
  readonly claims = this._claims.asReadonly();

  /** Inicia o fluxo OIDC (redirect). Stub. */
  login(_returnUrl?: string): void {
    this._status.set('authenticating');
  }

  /** Processa o callback OIDC (troca code por sessão). Stub. */
  async completeLogin(_code: string): Promise<void> {
    /* impl no ciclo da lib */
  }

  /** Renova o access token (rotation). Stub. */
  async refresh(): Promise<void> {
    /* impl no ciclo da lib */
  }

  /** Restaura sessão a partir do cookie httpOnly. Stub. */
  async restore(): Promise<void> {
    /* impl no ciclo da lib */
  }

  /** Logout (blacklist + limpa cookie). Stub. */
  async logout(): Promise<void> {
    this._status.set('anonymous');
    this._claims.set(null);
  }
}
