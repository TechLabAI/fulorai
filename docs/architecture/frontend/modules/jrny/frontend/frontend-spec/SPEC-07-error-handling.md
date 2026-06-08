# SPEC-07 — Error Handling — JRNY · Frontend

> Mapeamento `ProblemDetail` (RFC 7807, BE) → `AppError` (`@journeyos/shared/error-model`) → mensagem
> user-facing (`@journeyos/shared/ui-feedback`). Espelha `jrny-service/contracts/api-contract.md §5`.

## Mapa de `error.code` → UI

| HTTP | error.code | Mensagem FE | Apresentação |
|---|---|---|---|
| 422 | `jrny.jornada.nome-obrigatorio` | "Informe um nome para a jornada." | inline no campo nome |
| 422 | `jrny.jornada.sem-estagio` | "Adicione ao menos um estágio antes de publicar." | inline na `PublishBar` |
| 422 | `jrny.estagio.tipo-invalido` | "Tipo de estágio inválido." | inline no seletor de tipo |
| 422 | `jrny.regra.condicao-invalida` | "Condição inválida: revise os campos/operadores." | inline no `ConditionBuilder` |
| 422 | `jrny.regra.estagio-invalido` | "O estágio-destino não pertence a esta jornada." | inline no seletor de destino |
| 404 | `jrny.jornada.nao-encontrada` | "Jornada não encontrada." | estado vazio na página |
| 404 | `jrny.inscricao.nao-encontrada` | "Este lead ainda não entrou em nenhuma jornada." | estado vazio (decision log) |
| 409 | `jrny.jornada.transicao-invalida` | "Esta jornada já está publicada — crie uma nova versão para editar." | banner + CTA "criar nova versão" |
| 409 | `jrny.estagio.ordem-duplicada` | "Já existe um estágio nessa posição." | inline no campo ordem |
| 401 | `jrny.auth.token-invalido` | (sessão expirada) | redireciona ao login (Access Layer) |
| 403 | `jrny.acesso.permissao-negada` | "Você não tem permissão para esta ação." | bloqueio amigável (ação já escondida pelo guard) |
| — | **IA indisponível** (`assistIa = INDISPONIVEL`) | "Roteamento determinístico" | **badge neutro** — **não é erro** |

## Estratégia de retry

- **Leituras** (lista, builder, regras, decisões, analytics): falha de rede → estado de erro com botão
  **"Tentar novamente"** (retry manual), via `@journeyos/shared/ui-feedback`.
- **Mutações** (criar/publicar/arquivar/nova-versão/regra): sem retry automático; a UI reexibe a ação e
  o erro mapeado. Erros de validação (422/409) são **inline**, não toast.
- **Reordenar estágio** (otimista): falha do `PATCH` → **rollback** da ordem em tela + toast de erro.

## Toast vs banner vs modal

- **Inline (campo)** — erros de validação de formulário (422/409 de campo).
- **Banner (topo da página)** — `409 transicao-invalida` (com CTA nova versão); falha de leitura.
- **Toast** — sucesso de mutação (publicada/arquivada) e falha de reordenação otimista.
- **Modal** — apenas confirmações destrutivas (arquivar jornada).
- **Nunca toast/erro** para `assistIa = INDISPONIVEL|IGNORADO` (degradação graciosa, ADR-005).

## Critérios de aceite (EARS)

- `WHEN the BE returns a ProblemDetail, THE SYSTEM SHALL map it to an AppError via @journeyos/shared/error-model before rendering.`
- `IF publish fails with jrny.jornada.sem-estagio, THEN THE SYSTEM SHALL show an inline message on the publish bar and SHALL NOT navigate away.`
- `IF an edit fails with jrny.jornada.transicao-invalida, THEN THE SYSTEM SHALL show a banner offering "criar nova versão" instead of a raw error.`
- `IF a stage reorder PATCH fails, THEN THE SYSTEM SHALL roll back the optimistic order and show an error toast.`
- `WHEN assistIa is INDISPONIVEL, THE SYSTEM SHALL render a neutral badge and SHALL NOT render any error UI.`
- `IF a read request fails, THEN THE SYSTEM SHALL render an error state with a manual "tentar novamente" action.`

## Referências
- BE `contracts/api-contract.md §5` · `@journeyos/shared/error-model` · `ui-feedback`
- `05-state-and-data-flow.md` §5 · `adr/ADR-005-canvas-builder-rendering.md`
