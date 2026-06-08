import { Injectable, signal } from '@angular/core';

// @journeyos/shared/empresa-context — Wave-0 API surface (stub).
// ÚNICA fonte da verdade do empresaId ativo no FE. Nunca ler empresaId do JWT decodificado.

export interface EmpresaRef {
  empresaId: string;
  nome: string;
  papel: string;
}

@Injectable({ providedIn: 'root' })
export class EmpresaContextService {
  private readonly _current = signal<EmpresaRef | null>(null);
  private readonly _disponiveis = signal<EmpresaRef[]>([]);

  /** Empresa ativa (contexto atual). */
  readonly current = this._current.asReadonly();
  /** Empresas que o usuário pode operar. */
  readonly disponiveis = this._disponiveis.asReadonly();

  /** WRKS alimenta a lista de empresas. */
  setDisponiveis(empresas: EmpresaRef[]): void {
    this._disponiveis.set(empresas);
  }

  /**
   * Troca de empresa SEM reload: emite novo JWT, cancela in-flight da anterior,
   * invalida cache escopado e re-avalia navegação (ADR-005). Stub.
   */
  async switchTo(empresaId: string): Promise<void> {
    const found = this._disponiveis().find((e) => e.empresaId === empresaId);
    if (found) this._current.set(found);
  }

  /** Limpa o contexto (logout). */
  reset(): void {
    this._current.set(null);
    this._disponiveis.set([]);
  }
}
