# Plano de Execução — FE-JRNY (Journey & Routing · Frontend)

> Plano de implementação do FE JRNY (Layer 2). Âncora: `_brief.md` (orquestração de jornada) +
> `01-architectural-vision.md`. 28 issues (22 FE + 6 INT) em ondas P1..P9.

## Resumo

O JRNY é o **motor de jornada e roteamento** do Journey OS — o módulo FE **mais complexo**. A UI tem
dois lados: **autoria** (Journey Builder estruturado + Routing Engine versionado) e **auditoria**
(decision log explicável). O FE **decide e sinaliza, não executa**: desenha jornadas/estágios/regras e
**lê** estado/decisões; nunca dispara mensagem/oferta (COMM/SALE) nem roteia manualmente. A IA
(`orchestration`) é assist BE-side, refletida como badge ternário (`USADO`/`IGNORADO`/`INDISPONIVEL`),
com degradação graciosa (neutro, nunca erro). Decisão crítica: **editor estruturado de estágios
ordenados** (ADR-005), sem lib de canvas no MVP.

## Mapa P1–P9

| Onda | Entrega | Issues | Estimativa |
|---|---|---|---|
| **P1** | Module entry + contrato + registro Shell | 001, 002, 003 | ~2 dias |
| **P2** | Data access (journey/stage/rule/query) + erros | 004–008 | ~6 dias |
| **P3** | 6 features + ui local + sortable | 009–016 | ~12 dias |
| **P4** | Integrações Access Layer + runtime | INT-001..006 | ~5 dias |
| **P5** | Guards (auth/empresa/access) | 017 | ~1 dia |
| **P6** | Navegação/breadcrumbs | 018 | ~1 dia |
| **P7** | UX polish + flags + a11y | 019, 020 | ~3 dias |
| **P8** | Observability | 021 | ~1 dia |
| **P9** | e2e + hardening | 022 | ~2 dias |

## Caminho crítico

```
001 → 002 → INT-001 → 004 → 005 → 010 → 016 → 019 → 020 → 022
```

Builder (010) + sortable acessível com rollback (016) são o núcleo de risco/esforço. Após P2, as
trilhas regras (012), decision-log (013), analytics (014) e stage-editor (011) correm em paralelo.

## Riscos top-3 (do 06-risks)

1. **R1 — Decisão como caixa-preta / IA-off tratada como erro.** Mitigação: ADR-005 + FE-JRNY-013/015
   (decision log sempre explicável; badge neutro para IGNORADO/INDISPONIVEL).
2. **R2 — Over-engineering do builder (canvas pesado).** Mitigação: ADR-005 + FE-JRNY-010/016/020
   (editor estruturado; flag `journey-builder-canvas` off; sem lib de canvas).
3. **R3 — UI muta jornada PUBLICADA.** Mitigação: gate `RASCUNHO` em FE-JRNY-010 (read-only + CTA nova
   versão; espelha `409 transicao-invalida`).

## Definition of Done por onda

- **P1:** `JRNY_MODULE_DESCRIPTOR` registrado; menu "Jornadas" no Shell; `build/lint journey-os-web` ✅.
- **P2:** facades expõem signals readonly; `nx test/lint/build jrny-data-access` ✅; erros mapeados.
- **P3:** 6 features navegáveis; builder read-only quando publicado; decision log explicável; `nx test/lint/build` das libs ✅.
- **P4:** http-base + empresa-invalidation + access/nav + runtime registry ligados; isolamento cross-empresa.
- **P5–P6:** guards bloqueiam sem-empresa/sem-perm; breadcrumbs corretos.
- **P7:** estados loading/empty/error + retry; flags efetivas; a11y AA.
- **P8:** telemetria sem PII.
- **P9:** 7 specs Playwright verdes; bundle no budget; a11y sem violações críticas.

## Approval criteria por marco

- **P3 done = MVP shippable em dev?** Sim para o núcleo (autoria + auditoria): criar/publicar jornada,
  versionar regras, ler decisões explicáveis. Analytics (014) depende do gap G1 (endpoint) — degrada
  para vazio sem bloquear. Guards/flags/e2e (P5–P9) endurecem o release.
- **Pós-P9:** módulo pronto para integração de release com WRKS (auth) + LEAD (eventos que disparam
  roteamento, BE-side).

## Referências

- `_brief.md` · `01..06` · `frontend-spec/SPEC-01..08` · `adr/ADR-001..005` · `issues/issues_map.md`
- BE: `jrny-service/contracts/{api-contract,data-model,event-contracts}.md`
