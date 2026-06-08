# Plano de Execução — FE-COMM (Communication Hub · Frontend)

> Plano de implementação do FE COMM (Layer 2). Âncora: `_brief.md` + `01-architectural-vision.md`.
> Total: 26 issues (20 FE + 6 INT) em ondas P1–P9.

## Resumo

O COMM dá a Marina (Head de Growth) e Lucas (SDR) a superfície única para falar com leads de forma
padronizada e rastreável: catálogo de **templates** versionados (com placeholders e Template Studio/IA),
**regras de roteamento**, **disparo idempotente** e **rastreio do ciclo de vida** da mensagem em tempo
quase real (polling — ADR-005), além de **config de canais** por empresa. O FE consome apenas o
`comm-service`, nunca conhece provedores (só `canal`) e delega 100% da IA ao BE (degradação graciosa do
Studio). Depende de WRKS (auth/empresa/RBAC) e lê assets do ASST apenas via API BE.

## Mapa P1–P9 (estimativa por onda)

| Onda | Conteúdo | Issues | Estimativa |
|---|---|---|---|
| P1 | Foundation: contract, routes/lazy, descriptor+registro Shell | 001–003 | ~2 dias |
| P2 | Data access: Template/Studio/Routing/Message/Channel facades + erro | 004–008 | ~6 dias |
| P3 | Features: catálogo, editor, studio, roteamento, mensagens (lista+detalhe), canais | 009–015 | ~10 dias |
| P4 | Integrações Hub: http-base, auth/empresa, access-decision, navigation, shell-runtime, error-model | INT-001–006 | ~5 dias |
| P5 | Access guards | 016 | ~0,5 dia |
| P6 | Navigation / breadcrumbs | 017 | ~0,5 dia |
| P7 | UX polish (loading/empty/error + tokens) | 018 | ~1,5 dia |
| P8 | Observability | 019 | ~0,5 dia |
| P9 | e2e Playwright + perf/a11y | 020 | ~3 dias |

## Caminho crítico

```
001 → 002 → INT-001 → 007 → 013 → 014 → 018 → 020
```
Ramos paralelos após P2: templates (004→009→010→005→011), roteamento (006→012), canais (008→015).

## Riscos top-3 (do 06-risks)

1. **R1/R2 — Polling de entrega** (carga/latência/leaks): mitigado por ADR-005 (backoff + parada no
   terminal/destroy + flag), concentrado em FE-COMM-007/014.
2. **R3 — Degradação da IA confundida com falha**: banner explícito + flag, em FE-COMM-011 + e2e.
3. **R8/R9 — Vazamento de provedor/segredo na UI**: FE só modela `canal`; `credencialRef` mascarada
   (FE-COMM-015, UINV-6).

## Definition of Done por onda

- **P1:** Shell lista "Comunicação"; rotas resolvem (stubs); `build/lint journey-os-web` verdes.
- **P2:** facades expõem signals readonly; polling/idempotência/degradação testados; `nx test/lint comm-data-access` PASS.
- **P3:** 5 features navegáveis com dados reais; golden paths funcionam; `nx build` por feature PASS.
- **P4:** auth/empresa/permissão/erro/nav integrados à Access Layer; troca de empresa isola + para polling.
- **P5–P8:** guards, breadcrumbs, polish (a11y), telemetria sem PII.
- **P9:** 9 fluxos e2e passam (incl. gaps C-05.4/C-06.4); perf budget + axe OK.

## Approval criteria por marco

- **P3 done = MVP shippable em dev?** Sim para o golden path (autoria → ativar → disparar → rastrear)
  com WRKS disponível; roteamento/canais configuráveis. Falta hardening (P5–P9) para produção.

## Referências

- `_brief.md` · `01..06` · `frontend-spec/SPEC-01..08` · `contracts/*` · ADR-001..005
- `issues_map.md` (índice + caminho crítico + cobertura de gaps)
- BE: `comm-service/contracts/api-contract.md`
