# SPEC-08 — E2E Scenarios — ASST · Frontend

> Cenários e2e (Gherkin) que viram `.feature` em `e2e/` e specs Playwright em `apps/asst-e2e/`
> (gerados pelo `@journeyos/internal:module`). Cobrem golden path, degradação da IA, workflow,
> isolamento multi-empresa, RBAC e deep link.

## Lista de cenários → arquivos `.feature`

| Arquivo | Foco | Invariantes cobertas |
|---|---|---|
| `asset-lifecycle.feature` | Golden path: criar → (compor) → nova versão → submeter → aprovar → publicar; imutabilidade | UINV-4, UINV-5, evento-âncora |
| `asset-studio-degradation.feature` | Asset Studio compõe rascunho; IA indisponível (`503`) degrada graciosamente | UINV-7, ADR-005 |
| `approval-workflow.feature` | Fila de aprovação: aprovar e rejeitar (comentário obrigatório); transição inválida | UINV-5, UINV-6 |
| `empresa-isolation.feature` | Troca de empresa invalida catálogo; nenhum asset cross-empresa vaza | UINV-8, R-2 (LGPD) |
| `entitlement-denied.feature` | Persona sem permissão não vê/usa ações (criar/aprovar/publicar) | UINV-2 |
| `deep-link.feature` | Acesso direto a `/asst/assets/:id` e `/asst/approvals` respeita guards | UINV-1 |

## Resumo dos cenários (detalhe completo nos `.feature`)

### asset-lifecycle.feature (golden path)
- Marina cria um asset `EMAIL` → estado `RASCUNHO`.
- Cria uma versão manual com conteúdo → versão 1 (`origem=MANUAL`).
- Submete → `EM_REVISAO`; Rafael aprova → `APROVADO`; Rafael publica → `PUBLICADO`, versão vigente = 1.
- Tentativa de editar a versão publicada → bloqueada; só "criar nova versão" é oferecido (UINV-4).

### asset-studio-degradation.feature
- Marina abre o Asset Studio, informa um brief → composição → nova versão `RASCUNHO` (`origem=ASSET_STUDIO`).
- Com a IA indisponível (`503 asst.studio.ia-indisponivel`): banner de degradação, **nenhuma versão
  criada**, CTA "compor manualmente"; catálogo e aprovação seguem funcionando (UINV-7).

### approval-workflow.feature
- Rafael vê a fila de aprovações (assets `EM_REVISAO`).
- Aprova um asset (comentário opcional) → `APROVADO`.
- Rejeita outro **sem comentário** → bloqueado (comentário obrigatório na rejeição — UINV-6); com
  comentário → `REJEITADO`, volta para autoria.
- Tentar publicar um asset não-`APROVADO` → ação não disponível (UINV-5).

### empresa-isolation.feature
- Com empresa A ativa, catálogo mostra assets de A.
- `switchTo(B)` → catálogo de A é invalidado antes de renderizar; nenhum asset de A aparece sob B (R-2).

### entitlement-denied.feature
- Lucas (`SDR`, sem `asst.asset.criar`/`aprovar`) entra no catálogo: vê assets publicados, **não** vê
  os botões "Novo asset", "Aprovar", "Publicar" nem o deep link "Aprovações" (UINV-2).

### deep-link.feature
- Acesso direto a `/asst/assets/:id` sem sessão → redirecionado para login (UINV-1).
- Acesso direto a `/asst/approvals` sem `asst.asset.aprovar` → bloqueado pelo `accessGuard`.

## Notas
- Os `.feature` usam `# language: pt` (Gherkin pt-BR), padrão do WRKS.
- No A4/A5, cada `.feature` vira um spec stub `*.spec.ts` (`test.fixme`) discoverável/compilável; a
  implementação real dos fluxos é a wave P9 do `/fe-implement`.

## Referências
- `01-architectural-vision.md` §7 (success signals) · `03-domain-framing-frontend.md` (UINV)
- WRKS SPEC-08 + `e2e/*.feature` (padrão)
