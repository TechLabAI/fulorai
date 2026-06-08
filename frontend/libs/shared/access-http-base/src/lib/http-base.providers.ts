import {
  EnvironmentProviders,
  Provider,
  makeEnvironmentProviders,
} from '@angular/core';

// @journeyos/shared/access-http-base — Wave-0 API surface (stub).
// HttpClient + interceptors (Correlation, X-Empresa-Id, ErrorNormalize). Configurado no Shell.
// Toda chamada HTTP dos módulos passa por aqui (nunca HttpClient cru em componentes).

export interface HttpBaseConfig {
  /** Base URL do API gateway. */
  baseUrl?: string;
}

/**
 * Provê o stack HTTP base da plataforma (a chamar uma vez no Shell: `provideHttpBase({...})`).
 * Stub: registra os interceptors reais no ciclo da lib.
 */
export function provideHttpBase(_config: HttpBaseConfig = {}): EnvironmentProviders {
  const providers: Provider[] = [
    // TODO: provideHttpClient(withInterceptors([correlation, empresaId, errorNormalize]))
  ];
  return makeEnvironmentProviders(providers);
}
