# SPEC-08 — E2E Scenarios — JRNY · Frontend

> Cenários e2e (Gherkin, pt-BR). Cada arquivo vira um `.feature` em `e2e/`, copiado pelo
> `@journeyos/internal:module` para `apps/jrny-e2e/src/specs/`. Cada cláusula SHALL de SPEC-01..07 tem
> cobertura aqui (gate A2.5 `fe-architect-specs-validate`).

## Cenários e arquivos

| Arquivo `.feature` | Foco | Cobre (EARS de) |
|---|---|---|
| `journey-authoring.feature` | golden path A: criar rascunho → adicionar/reordenar estágios → publicar | SPEC-01 (redirect, lazy), SPEC-02 (reorder a11y), SPEC-03 (editavel/podePublicar) |
| `journey-publish-guards.feature` | publicar sem estágio; editar PUBLICADA → nova versão; ordem duplicada | SPEC-01 (read-only), SPEC-03, SPEC-07 (sem-estagio, transicao-invalida, ordem-duplicada) |
| `routing-rules.feature` | criar regra versionada; editar bumpa versão; condição inválida | SPEC-04 (versão), SPEC-07 (condicao-invalida, estagio-invalido) |
| `decision-log-explainability.feature` | golden path B: trilha de decisões explicável + badge assist (USADO/IGNORADO/INDISPONIVEL) | SPEC-02/03 (badge), SPEC-07 (IA indisponível neutro) |
| `empresa-switch-isolation.feature` | troca de empresa invalida jornadas/builder | SPEC-04 (invalidação), SPEC-06 (bootstrap) |
| `entitlement-denied.feature` | rota/ação sem permissão escondida/negada | SPEC-01 (accessGuard), SPEC-05 (gating) |
| `deep-link.feature` | deep-link direto a builder/decisões; redirect raiz; analytics flag | SPEC-01 (deep link, redirect, flag) |

## Cobertura EARS → Gherkin (resumo)

- **Redirect raiz** (`/jrny` → `/jrny/journeys`) → `deep-link.feature`.
- **empresaGuard / accessGuard** → `entitlement-denied.feature`, `deep-link.feature`.
- **Read-only de PUBLICADA + nova versão** → `journey-publish-guards.feature`.
- **Publicar exige ≥1 estágio** → `journey-publish-guards.feature`.
- **Reordenação por teclado/ponteiro** → `journey-authoring.feature`.
- **Decisão sempre explicável + badge neutro p/ IA-off** → `decision-log-explainability.feature`.
- **Bumpa versão na edição de regra** → `routing-rules.feature`.
- **Flag journey-analytics oculta rota/menu** → `deep-link.feature`.
- **Invalidação na troca de empresa** → `empresa-switch-isolation.feature`.

## Notas

- Os `.feature` são **estruturais** no MVP (gate A5 = `--list`/compilação; execução real dos fluxos é
  da wave de implement P9). Sem lógica de negócio ainda — os specs Playwright nascem como stubs
  descobríveis.
- pt-BR (`# language: pt`), espelhando os demais módulos.

## Referências
- `e2e/*.feature` · `SPEC-01..07` · `adr/ADR-005-canvas-builder-rendering.md`
