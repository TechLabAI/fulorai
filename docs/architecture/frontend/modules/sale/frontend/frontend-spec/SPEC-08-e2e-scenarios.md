# SPEC-08 — E2E Scenarios — SALE · Frontend

> Cenários e2e (Gherkin, pt-BR). Cada arquivo vira um `.feature` em `e2e/`, copiado pelo
> `@journeyos/internal:module` para `apps/sale-e2e/src/specs/`. Cada cláusula SHALL de SPEC-01..07 tem
> cobertura aqui (gate A2.5 `fe-architect-specs-validate`).

## Cenários e arquivos

| Arquivo `.feature` | Foco | Cobre (EARS de) |
|---|---|---|
| `pipeline-kanban-move.feature` | golden path: abrir pipeline → arrastar oportunidade ao próximo estágio → optimistic update persistido | SPEC-01 (redirect, lazy), SPEC-02 (drag/optimistic), SPEC-03 (arrastavel), SPEC-04 (snapshot/rollback) |
| `opportunity-win-loss.feature` | ganhar; perder exige motivo → `422` exibido inline; deal fechada é terminal | SPEC-02 (terminal), SPEC-03 (podeFechar), SPEC-07 (motivo-obrigatorio, ja-fechada) |
| `offer-versioning.feature` | editar oferta cria nova versão; versões anteriores imutáveis; preço inválido | SPEC-01 (rotas oferta), SPEC-04 (nova versão), SPEC-07 (preco-invalido) |
| `purchase-attribution-breakdown.feature` | abrir compra → ver breakdown explicável + LTV; sem criação de compra no FE | SPEC-02 (breakdown), SPEC-03 (Σ=valorTotal), SPEC-04 (no create-compra) |
| `attribution-model-activate.feature` | ativar versão re-atribui; fallback LAST_TOUCH enquanto nenhuma ativa; soma inválida | SPEC-03 (fallback), SPEC-04 (re-atribuição), SPEC-07 (soma-invalida) |
| `empresa-switch-isolation.feature` | troca de empresa invalida pipeline/listas em tela | SPEC-04 (invalidação), SPEC-06 (bootstrap) |
| `entitlement-denied.feature` | rota/ação sem permissão escondida/negada | SPEC-01 (accessGuard), SPEC-05 (gating), SPEC-06 (filtro de menu) |
| `deep-link.feature` | deep-link direto a `/sale/opportunities/:id`; redirect raiz; flag revenue-dashboard | SPEC-01 (deep link, redirect, flag), SPEC-05 (flag) |

## Cobertura EARS → Gherkin (resumo)

- **Redirect raiz** (`/sale` → `/sale/pipeline`) → `pipeline-kanban-move.feature`, `deep-link.feature`.
- **empresaGuard / accessGuard** → `entitlement-denied.feature`, `deep-link.feature`.
- **Move otimista + rollback (`409 ja-fechada`)** → `pipeline-kanban-move.feature`, `opportunity-win-loss.feature`.
- **Perder exige motivo (`422`)** → `opportunity-win-loss.feature`.
- **Fechamento terminal (card não arrastável)** → `opportunity-win-loss.feature`.
- **Editar oferta cria nova versão / preço inválido** → `offer-versioning.feature`.
- **Breakdown explicável + Σ=valorTotal + sem create-compra** → `purchase-attribution-breakdown.feature`.
- **Ativar modelo re-atribui / fallback LAST_TOUCH / soma inválida** → `attribution-model-activate.feature`.
- **Invalidação na troca de empresa** → `empresa-switch-isolation.feature`.
- **Flag revenue-dashboard oculta rota/menu** → `deep-link.feature`.

## Notas

- Os `.feature` são **estruturais** no MVP (gate A5 = `--list`/compilação; execução real dos fluxos é
  da wave de implement). Sem lógica de negócio ainda — os specs Playwright nascem como stubs descobríveis.
- pt-BR (`# language: pt`), espelhando os demais módulos.

## Referências
- `e2e/*.feature` · `SPEC-01..07` · `adr/ADR-005-kanban-pipeline-rendering.md`
