# SPEC-07 — Error Handling — SALE · Frontend

> Mapeamento `ProblemDetail` (RFC 7807, BE) → `AppError` (`@journeyos/shared/error-model`) → mensagem
> user-facing (`@journeyos/shared/ui-feedback`). Espelha `sale-service/contracts/api-contract.md` (Error catalogue).

## Mapa de `error.code` → UI

| HTTP | error.code | Mensagem FE | Apresentação |
|---|---|---|---|
| 422 | `sale.oportunidade.motivo-obrigatorio` | "Informe o motivo da perda." | inline no campo motivo do `LoseOpportunityDialog` |
| 409 | `sale.oportunidade.ja-fechada` | "Esta oportunidade já foi fechada — não é possível movê-la ou fechá-la de novo." | **rollback do Kanban** + toast (move otimista) · banner no detalhe |
| 404 | `sale.oportunidade.nao-encontrada` | "Oportunidade não encontrada." | estado vazio na página |
| 422 | `sale.oferta.preco-invalido` | "Preço inválido: informe um valor maior ou igual a zero." | inline no campo preço |
| 422 | `sale.compra.base-legal-invalida` | "Base legal ausente ou inválida para esta compra." | banner no detalhe (consulta) — informativo |
| 422 | `sale.compra.receita-inconsistente` | "A receita da compra está inconsistente com seus itens." | banner no detalhe (consulta) — informativo |
| 404 | `sale.compra.nao-encontrada` | "Compra não encontrada." | estado vazio na página |
| 404 | `sale.atribuicao.modelo-nao-encontrado` | "Versão de modelo de atribuição não encontrada." | inline na linha do modelo |
| 409 | `sale.atribuicao.soma-invalida` | "Não foi possível ativar: a soma atribuída não fecha com a receita." | banner na tela de atribuição |
| 401 | `iam.token-invalido` | (sessão expirada) | redireciona ao login (Access Layer) |
| 403 | `iam.permissao-negada` | "Você não tem permissão para esta ação." | bloqueio amigável (ação já escondida pelo guard) |

## Estratégia de retry

- **Leituras** (pipeline, oportunidade, ofertas, compras, atribuição, dashboard): falha de rede →
  estado de erro com botão **"Tentar novamente"** (retry manual), via `@journeyos/shared/ui-feedback`.
- **Mutações** (criar/ganhar/perder/editar oferta/estornar/cancelar/criar-ativar modelo): sem retry
  automático; a UI reexibe a ação e o erro mapeado. Erros de validação (422/409) são **inline/banner**, não toast.
- **Mover estágio no Kanban** (otimista, ADR-005): falha do `PATCH` (`409 ja-fechada`, rede, `403`) →
  **rollback** do card para a coluna de origem (último snapshot confirmado) + toast de erro.

## Toast vs banner vs modal

- **Inline (campo)** — erros de validação de formulário (`motivo-obrigatorio`, `preco-invalido`, `modelo-nao-encontrado`).
- **Banner (topo da página)** — `soma-invalida` (atribuição); `base-legal-invalida`/`receita-inconsistente`
  (informativos no detalhe da compra); falha de leitura.
- **Toast** — sucesso de mutação (ganhou/perdeu/estornou) e **falha do move otimista do Kanban** (com rollback).
- **Modal** — confirmações destrutivas: **estornar**/**cancelar** compra; e o `409 ja-fechada` no detalhe
  da oportunidade aparece como banner explicativo após a ação.

## Critérios de aceite (EARS)

- `WHEN the BE returns a ProblemDetail, THE SYSTEM SHALL map it to an AppError via @journeyos/shared/error-model before rendering.`
- `IF a stage move fails with sale.oportunidade.ja-fechada, THEN THE SYSTEM SHALL roll back the optimistic Kanban move and show an error toast.`
- `IF marking an opportunity as lost fails with sale.oportunidade.motivo-obrigatorio, THEN THE SYSTEM SHALL show an inline message on the motivo field and SHALL NOT close the opportunity.`
- `IF activating an attribution model fails with sale.atribuicao.soma-invalida, THEN THE SYSTEM SHALL show a banner and SHALL NOT mark the version active.`
- `IF editing an offer fails with sale.oferta.preco-invalido, THEN THE SYSTEM SHALL show an inline price error and SHALL NOT create a new version.`
- `IF a read request fails, THEN THE SYSTEM SHALL render an error state with a manual "tentar novamente" action.`

## Referências
- BE `contracts/api-contract.md` (Error catalogue) · `@journeyos/shared/error-model` · `ui-feedback`
- `05-state-and-data-flow.md` · `adr/ADR-005-kanban-pipeline-rendering.md`
