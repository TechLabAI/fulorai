# Plano de Execução — FE-SALE (Sales & Revenue · Frontend)

> Plano de implementação do FE SALE (Layer 2). Âncora: `_brief.md` (pipeline único + receita rastreável)
> + `01-architectural-vision.md`. 29 issues (23 FE + 6 INT) em ondas P1..P9.

## Resumo

O SALE é o **funil de receita rastreável** do Journey OS: dá ao closer (Lucas/SDR), ao infoprodutor
(Rafael) e à Head de Growth (Marina) uma **superfície única** para operar o **pipeline de vendas num
Kanban** (oportunidades movendo por estágio via drag-and-drop), **ganhar/perder** com motivo, catalogar
**ofertas versionadas**, consultar **compras** confirmadas com seu **breakdown de atribuição explicável**,
governar **modelos de atribuição** versionados e ler um **dashboard de receita** (funil + LTV). O golden
path é "Compra confirmada": *abrir Kanban → mover estágio → ganhar → compra confirmada (server-to-server)
→ receita atribuída → LTV atualizado*. A UI **não** registra compra (ingestão server-to-server) e **não**
chama IA no MVP — atribuição e LTV são determinísticos e explicáveis. Decisão crítica: **Kanban com CDK
DragDrop, optimistic move + rollback obrigatório** (ADR-005), o nó de maior valor/risco.

## Mapa P1–P9

| Onda | Entrega | Issues | Estimativa |
|---|---|---|---|
| **P1** | Module entry + contrato + descriptor + registro Shell + integration/bootstrap | 001–004 | ~2,5 dias |
| **P2** | Data access (oportunidade/oferta/compra/atribuição+ltv) + erros | 005–009 | ~7 dias |
| **P3** | 6 features + ui local + flag multi-touch | 010–017 | ~13 dias |
| **P4** | Integrações Access Layer + runtime + erro + observability | INT-001..006 | ~5 dias |
| **P5** | Guards (auth/empresa/access) | 018 | ~1 dia |
| **P6** | Navegação/breadcrumbs | 019 | ~1 dia |
| **P7** | UX polish + rollback UX + a11y/perf do board | 020, 021 | ~3 dias |
| **P8** | Observability | 022 | ~1 dia |
| **P9** | e2e (8 specs) + hardening | 023 | ~2 dias |

## Caminho crítico

```
001 → 002 → INT-001 → 005 → 010 → 020 → 021 → 022 → 023
```

Kanban (010) com optimistic move + rollback é o núcleo de risco/esforço; FE-SALE-016 (ui board/chips)
precede as features P3. Após P2, as trilhas oferta (012), compra (013), atribuição (014), dashboard
(015), guards (018) e navegação (019) correm em paralelo.

## Riscos top-3 (do 06-risks)

1. **R1 — Drag-and-drop inconsistente (card "preso" sem rollback).** Mitigação: ADR-005 + FE-SALE-005
   (snapshot) + FE-SALE-010 (optimistic + rollback obrigatório) + FE-SALE-020 (UX do rollback) + e2e
   `pipeline-kanban-move` cobrindo `409 ja-fechada` e falha de rede.
2. **R4 — Atribuição lida como caixa-preta (só o total).** Mitigação: `AttributionBreakdownComponent`
   **sempre** com touchpoint + tipo + valor + versão de modelo e Σ = valorTotal (FE-SALE-013/014/016);
   e2e `purchase-attribution-breakdown`.
3. **R2/R3 — Performance e bundle do Kanban (centenas de cards + CDK + chart + 6 features).** Mitigação:
   virtual scroll/paginação por coluna (FE-SALE-021), CDK DragDrop só no feature-pipeline, chart de funil
   leve (SVG/CSS) e lazy por rota (FE-SALE-002/015).

> Riscos complementares: R5 (sem create-compra — FE-SALE-007/013), R8 (isolamento cross-empresa —
> INT-FE-SALE-002), R9 (LGPD na compra — FE-SALE-013), R7 (efeito de ativar modelo/estorno — FE-SALE-014).

## Definition of Done por onda

- **P1:** `SALE_MODULE_DESCRIPTOR` registrado; menu "Vendas" no Shell; `build/lint journey-os-web` ✅;
  contrato com 15 perms + 2 flags consistente com BE.
- **P2:** facades expõem signals readonly; snapshot/rollback do move pronto; **sem create-compra**;
  erros mapeados (9 códigos SALE); `nx test/lint/build sale-data-access` ✅.
- **P3:** 6 features navegáveis; Kanban com optimistic+rollback; breakdown sempre explicável; oferta
  versionada (editar = nova versão); dashboard flag-gated degrada; `nx test/lint/build` das libs ✅.
- **P4:** http-base+JWT + empresa-invalidation + access/entitlement + runtime registry + error-model +
  observability ligados; isolamento cross-empresa.
- **P5–P6:** guards bloqueiam sem-empresa/sem-perm; breadcrumbs (incl. detalhe com param) corretos.
- **P7:** estados loading/empty/error + retry; UX do rollback (toast + retorno do card); flag dashboard
  efetiva; a11y AA + DnD por teclado; virtual scroll por coluna.
- **P8:** telemetria (board/move/win-loss/estorno) sem PII.
- **P9:** 8 specs Playwright verdes; bundle no budget; a11y sem violações críticas.

## Approval criteria por marco

- **P3 done = MVP shippable em dev?** Sim para o núcleo operacional: operar o pipeline (Kanban +
  optimistic/rollback), ganhar/perder, catalogar ofertas versionadas, consultar compras com breakdown
  explicável, governar modelos de atribuição. O **dashboard de funil** depende do gap G1 (endpoint
  `/receita/funil`) — degrada para LTV-apenas/vazio sem bloquear; multi-touch (G4) fica atrás de flag.
  Guards/flags/e2e (P5–P9) endurecem o release.
- **Pós-P9:** módulo pronto para integração de release com WRKS (auth/empresa/RBAC) + LEAD (evento
  `lead.qualificado` que cria a oportunidade, BE-side) + INTL (analytics de receita, soft, só via API BE).

## Referências

- `_brief.md` · `06-risks-gaps-assumptions.md` · `frontend-spec/SPEC-01..08` · `contracts/backend-api-cross-link.md`
- `adr/ADR-004` (shell-integration) · `adr/ADR-005` (kanban + optimistic move) · `issues/issues_map.md`
- BE: `sale-service/contracts/{api-contract,data-model}.md` · `adr/ADR-005-revenue-attribution-model.md`
