# SPEC-07 — Error Handling — ASST · Frontend

> Mapeamento `ProblemDetail` (BE, RFC 7807) → `AppError` (`@journeyos/shared/error-model`) →
> mensagem user-facing (`@journeyos/shared/ui-feedback`). Fonte de códigos: `asst-service/contracts/api-contract.md` §5.

## Pipeline

```
asst-service → ProblemDetail { type, title, status, detail, code, correlationId }
   → interceptor (access-http-base) normaliza
   → toAppError() → AppError { code, title, detail, field? }
   → facade expõe error() signal (e studioState='degradado' no caso da IA)
   → componente renderiza via ui-feedback (inline / toast / banner / página)
```

## Tabela de mapeamento (`code` BE → UI)

| HTTP | `code` (BE) | Mensagem FE (pt-BR) | Apresentação | Retry |
|---|---|---|---|---|
| 422 | `asst.asset.titulo-obrigatorio` | "Informe um título para o asset." | inline (campo `titulo`) | — |
| 422 | `asst.asset.tipo-invalido` | "Selecione um tipo de asset válido." | inline (campo `tipoAsset`) | — |
| 404 | `asst.asset.nao-encontrado` | "Asset não encontrado." | página (estado vazio no detalhe) | botão "voltar ao catálogo" |
| 404 | `asst.asset.sem-versao-publicada` | "Este asset ainda não tem versão publicada." | banner informativo no detalhe | — |
| 409 | `asst.versao.imutavel` | "Versões publicadas não podem ser editadas. Crie uma nova versão." | toast | recarrega versões |
| 409 | `asst.estado.transicao-invalida` | "Esta ação não é permitida no estado atual do asset." | toast + esconde/desabilita a ação | recarrega asset |
| 503 | `asst.studio.ia-indisponivel` | "O Asset Studio está indisponível no momento. Você pode compor manualmente." | **banner de degradação** no Studio | botão "tentar novamente" + CTA "compor manualmente" |
| 403 | `asst.acesso.permissao-negada` | "Você não tem permissão para esta ação." | toast + esconde a ação | — |
| 401 | `asst.auth.token-invalido` | (silencioso) | refresh/login automático | automático (interceptor/auth-session) |
| 5xx | _genérico_ | "Algo deu errado. Tente novamente." | toast/banner | botão "tentar novamente" |

## Critério Toast vs Banner vs Modal vs Inline

- **Inline (no campo):** erros de validação `422` (título, tipo, URL de binário, comentário de rejeição).
- **Toast:** erros transitórios de ação (`409 transicao-invalida`, `409 imutavel`, `403`).
- **Banner:** estados persistentes de tela — `503 ia-indisponivel` no Studio (com CTA de fallback);
  `sem-versao-publicada` no detalhe.
- **Página/estado vazio:** `404 nao-encontrado` (asset inexistente).
- **Modal:** confirmações destrutivas (arquivar) — não é erro, mas usa o mesmo `ui-feedback`.

## Casos especiais

- **`503 asst.studio.ia-indisponivel` (degradação graciosa — ADR-005):** a facade do Studio seta
  `studioState='degradado'`, **não cria versão**, e a UI oferece "compor manualmente"
  (`POST /{id}/versoes`). O erro **nunca** propaga para bloquear catálogo/detalhe/aprovação (UINV-7).
- **`409 transicao-invalida`:** idealmente não ocorre (a UI deriva ações do estado — UINV-5); se ocorrer
  (estado mudou em outra aba), a UI recarrega o asset e re-deriva as ações.
- **Retry:** manual (botão) para ações de negócio; automático apenas para `401` (refresh de sessão).
  Composição do Studio: retry manual com `Idempotency-Key` para evitar dupla criação.

## Critérios de aceite (EARS)

> Notação EARS (D-057 / `be-validate-ears.py`). Backfill do gate A2.5. Derivados da tabela de
> mapeamento `code` BE → UI e dos casos especiais (degradação do Studio, transição inválida, retry).

- **A-07.1** `WHEN the BE returns a ProblemDetail, THE SYSTEM SHALL normalize it to an AppError through the shared error-model before display.`
- **A-07.2** `WHEN a request fails with the asset nao-encontrado error, THE SYSTEM SHALL show the asset-not-found page state with a link back to the catalog.`
- **A-07.3** `WHEN a request fails with a validation error, THE SYSTEM SHALL show the message inline on the offending field.`
- **A-07.4** `WHEN a Studio compose request fails with the ia-indisponivel error, THE SYSTEM SHALL show a degradation banner with a retry action and a compor-manualmente action.`
- **A-07.5** `IF a request fails with the estado transicao-invalida error, THEN THE SYSTEM SHALL reload the asset and re-derive its available actions.`
- **A-07.6** `IF a request fails with the permissao-negada error, THEN THE SYSTEM SHALL show a toast and SHALL hide the denied action.`
- **A-07.7** `THE SYSTEM SHALL provide a manual retry for business actions and SHALL NOT auto-retry mutating operations.`

## Referências
- BE: `asst-service/contracts/api-contract.md` §5 (ProblemDetail / códigos)
- `05-state-and-data-flow.md` §5 · `@journeyos/shared/error-model` · `@journeyos/shared/ui-feedback`
