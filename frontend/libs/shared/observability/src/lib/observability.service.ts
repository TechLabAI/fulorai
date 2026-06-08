import { Injectable } from '@angular/core';

// @journeyos/shared/observability — Wave-0 API surface (stub).
// Telemetria cross-cutting (timing de bootstrap, troca de empresa, ações). Minimizar PII (LGPD).

export interface ObservabilityEvent {
  name: string;
  payload?: Record<string, unknown>;
}

@Injectable({ providedIn: 'root' })
export class ObservabilityService {
  /** Emite um evento de telemetria. Stub (no-op até o ciclo da lib). */
  track(_event: ObservabilityEvent): void {
    /* impl no ciclo da lib */
  }

  /** Mede duração de uma operação nomeada. Stub. */
  timing(_name: string, _ms: number): void {
    /* impl no ciclo da lib */
  }
}
