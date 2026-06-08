// @journeyos/shared/error-model — Wave-0 API surface (stub).
// Mapeia ProblemDetail (RFC 7807) do BE para AppError consumível pela UI.

export interface ProblemDetail {
  type?: string;
  title: string;
  status: number;
  detail?: string;
  instance?: string;
  /** error.code canônico do Journey OS (ex.: 'wrks.usuario.duplicado'). */
  code?: string;
  [k: string]: unknown;
}

export interface AppError {
  /** error.code canônico (fonte da mensagem user-facing). */
  code: string;
  title: string;
  detail?: string;
  status?: number;
  /** campo do form associado, quando aplicável (ex.: 'email'). */
  field?: string;
}

/** Converte um ProblemDetail (ou erro cru) em AppError. Stub: implementação real no ciclo da lib. */
export function toAppError(input: ProblemDetail | unknown): AppError {
  const p = (input ?? {}) as Partial<ProblemDetail>;
  return {
    code: p.code ?? 'app.erro-desconhecido',
    title: p.title ?? 'Algo deu errado',
    detail: p.detail,
    status: p.status,
  };
}
