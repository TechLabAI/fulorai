# SPEC-08 — E2E Scenarios — LEAD · Frontend

> Cenários e2e (Gherkin) que viram `.feature` em `e2e/` e specs Playwright em `apps/lead-e2e/`
> (gerados pelo `@journeyos/internal:module`). Cobrem golden path, degradação do assist IA,
> segmentação, governança de regras, surveys, LGPD, isolamento multi-empresa, RBAC e deep link.

## Lista de cenários → arquivos `.feature`

| Arquivo | Foco | Critérios EARS cobertos |
|---|---|---|
| `lead-qualification.feature` | Golden path: fila priorizada → detalhe → breakdown 6D → requalificar | SPEC-01, SPEC-03, SPEC-04 |
| `maturity-score-degradation.feature` | Score com `assistIa=false` → badge "score determinístico" (não erro) | SPEC-03, SPEC-07, ADR-005 |
| `segmentation.feature` | Criar segmento → prévia de contagem → navegar à fila do segmento | SPEC-04 (Segment) |
| `qualification-rules.feature` | Criar versão (inativa) → ativar → versão ativa destacada; sem-regra-ativa | SPEC-04, SPEC-07 |
| `survey-capture.feature` | Responder survey de um lead → perfil atualizado → recálculo | SPEC-04 (Survey) |
| `lgpd-anonymization.feature` | Anonimizar lead → PII suprimida + edição/requalify travados | SPEC-07 (LGPD) |
| `empresa-switch-isolation.feature` | Troca de empresa invalida a fila; nenhum lead cross-empresa vaza | SPEC-04 |
| `entitlement-denied.feature` | SDR sem permissão não vê ações/deep links de governança | SPEC-01, SPEC-05 |
| `deep-link.feature` | Acesso direto a `/lead/leads/:id` e `/lead/qualification` respeita guards | SPEC-01 |

## Resumo dos cenários (detalhe completo nos `.feature`)

### lead-qualification.feature (golden path)
- Lucas abre `/lead/leads`: a fila está ordenada por Maturity Score desc.
- Filtra por segmento "Quentes"; seleciona um lead → abre o detalhe.
- O detalhe mostra as **6 dimensões** + `versaoRegra` + badge `IA ✓`.
- Clica "Requalificar" → o score é recalculado e o breakdown atualizado.

### maturity-score-degradation.feature
- Um lead cujo último score foi calculado **sem** assist de IA (`assistIa=false`).
- O detalhe mostra o badge neutro **"score determinístico"** (sem `IA ✓`), **sem** toast de erro; o
  fluxo segue normal (ADR-005).

### segmentation.feature
- Marina cria um segmento com um predicado válido → vê a **prévia de contagem**.
- Salva → o segmento aparece na lista; abrir o segmento navega à fila filtrada.
- Predicado inválido (`422 lead.segment.predicado-invalido`) → erro de campo, editor permanece aberto.

### qualification-rules.feature
- Marina cria uma nova versão de regra (estado **inativa**).
- Ativa a versão → ela passa a ser a **ativa** e a anterior é desativada.
- Com nenhuma regra ativa, "Requalificar" no detalhe fica desabilitado (`409 sem-regra-ativa`).

### survey-capture.feature
- Marina define um survey com perguntas; no detalhe de um lead, responde o survey.
- As respostas atualizam o perfil (`origem=SURVEY`) e disparam recálculo do score (BE).

### lgpd-anonymization.feature
- Lucas/Marina (com permissão) anonimiza um lead após **confirmação no modal**.
- O lead passa a `ANONIMIZADO`: PII suprimida; editar perfil e requalificar **desabilitados**
  (`409 lead.lead.anonimizado`).

### empresa-switch-isolation.feature
- Com empresa A ativa, a fila mostra leads de A.
- `switchTo(B)` → a fila de A é invalidada antes de renderizar; nenhum lead de A aparece sob B.

### entitlement-denied.feature
- Lucas (`SDR`, sem `lead.qualification.*`/`lead.segment.criar`) entra no módulo: vê a fila e o detalhe,
  **não** vê os deep links "Regras"/edição de segmentos nem o botão "Requalificar".

### deep-link.feature
- Acesso direto a `/lead/leads/:id` sem sessão → redirecionado para login.
- Acesso direto a `/lead/qualification` sem `lead.qualification.read` → bloqueado pelo `accessGuard`.

## Notas
- Os `.feature` usam `# language: pt` (Gherkin pt-BR), padrão do WRKS/ASST/INTL.
- No A4/A5, cada `.feature` vira um spec stub `*.spec.ts` (`test.fixme`) descobrível/compilável; a
  implementação real dos fluxos é a wave P9 do `/fe-implement`.
- Cada cláusula `THE SYSTEM SHALL` dos SPEC-01..07 tem cenário correspondente aqui (cobertura
  EARS→Gherkin validada no gate `/fe-architect-specs-validate`).

## Referências
- `01-architectural-vision.md` §7 (success signals) · `03-domain-framing-frontend.md` (invariantes)
- WRKS/ASST SPEC-08 + `e2e/*.feature` (padrão)
