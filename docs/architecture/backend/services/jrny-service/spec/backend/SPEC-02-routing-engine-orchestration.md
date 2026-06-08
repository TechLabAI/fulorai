# SPEC-02 — Routing Engine & Orchestration (core)

> Núcleo do domínio (evento-âncora: **lead roteado** — `journey-os.lead.roteado`). ADR-005
> (determinístico primeiro, assist opcional, decision log imutável), ADR-003 (mensageria/IA
> resiliente). EARS guide: `docs/architecture/backend/standards/ears-notation.md`.

## Objetivo

Especificar o **Routing Engine**: como, a cada evento de domínio de LEAD, JRNY avalia regras
versionadas (determinístico), opcionalmente consulta a TechLab AI (`orchestration`), decide o
estágio-alvo, matricula/avança a `inscricao_jornada`, grava uma `decisao_roteamento` imutável e
emite o evento-âncora — sempre reproduzível e auditável.

## Escopo

- **In:** consumo do gatilho (`lead.qualificado`/`score.atualizado`/`segmento.alterado`), construção do `snapshot_entrada`, avaliação determinística ordenada por `prioridade`, fold do assist de IA, matrícula/avanço, decision log, emissão de eventos, projeção Elastic.
- **Out:** definição de jornada/estágio/regra (SPEC-03), persistência detalhada (SPEC-04), idempotência/concorrência (SPEC-05), contrato do assist (SPEC-10 / `techlab-ai-integration.md`), execução de ações de canal/venda (COMM/SALE).

## Decisões técnicas

- `MotorRoteamento` é **domain service** (POJO, sem Spring/JPA, sem I/O) — avaliação pura e reproduzível (ADR-001/ADR-005).
- `RotearLeadService` (application, `@Transactional`) orquestra: carrega jornada PUBLICADA + inscrição, monta snapshot, chama `MotorRoteamento`, consulta `RecomendacaoIaPort` (opcional), persiste decisão, avança via `AvancarEstagioService`, enfileira eventos via outbox.
- **Determinístico primeiro:** regras ativas ordenadas por `prioridade` asc; a primeira satisfeita decide. A IA só refina e nunca sobrepõe uma regra de guarda obrigatória (ADR-005).
- **Assist opcional:** `RecomendacaoIaPort` com timeout curto + circuit breaker (Resilience4j); falha → `assist_ia=INDISPONIVEL`, fallback determinístico.
- **Decisão sempre registrada:** toda avaliação grava exatamente uma `decisao_roteamento` (ROTEADO/SEM_MUDANCA/NAO_ROTEADO), imutável.

## Fluxo (golden path)

```
lead.qualificado (Kafka)
  → fixa EmpresaContextHolder pelo header empresaId
  → carrega jornada PUBLICADA aplicável + inscricao_jornada (cria se ausente)
  → monta snapshot_entrada (score/dimensoes/segmento/atributos do payload LEAD)
  → MotorRoteamento avalia regras (asc por prioridade); (opcional) RecomendacaoIaPort
        → IA timeout/CB-aberto → assist_ia=INDISPONIVEL (decide só com regras)
  → decide estagio_alvo → AvancarEstagioService avança inscricao
  → grava DecisaoRoteamento (imutável) → projeta routing-decisions (best-effort)
  → emite lead.roteado (âncora) + estagio.transicionado → projeta journey-events (best-effort)
  → terminal? → estado=CONCLUIDA + emite jornada.concluida
```

## Casos de borda

- Nenhuma jornada PUBLICADA aplicável → decisão `NAO_ROTEADO`; sem evento de avanço.
- Reavaliação sem regra disparada → decisão `SEM_MUDANCA`; estágio mantido; sem `lead.roteado`.
- IA indisponível/timeout/circuito aberto → `assist_ia=INDISPONIVEL`; decisão segue só com regras.
- Regra de guarda obrigatória vs recomendação da IA → regra vence; `assist_ia=IGNORADO`.
- Estágio-alvo terminal → conclui a jornada (`jornada.concluida`).
- Reprocessamento do mesmo evento → idempotente (SPEC-05); sem matrícula/decisão duplicada.

## Critérios de aceite (EARS)

- `WHEN journey-os.lead.qualificado is consumed, THE SYSTEM SHALL evaluate the Routing Engine and persist exactly one decisao_roteamento (ROTEADO, SEM_MUDANCA or NAO_ROTEADO).`
- `THE SYSTEM SHALL evaluate active routing rules ordered by prioridade ascending and SHALL select the first rule whose condicao is satisfied.`
- `WHEN the result is ROTEADO, THE SYSTEM SHALL advance the inscricao_jornada to the target stage and emit journey-os.lead.roteado and journey-os.estagio.transicionado after commit.`
- `IF no PUBLICADA journey applies to the lead, THEN THE SYSTEM SHALL record a NAO_ROTEADO decision AND SHALL NOT emit journey-os.lead.roteado.`
- `WHEN a re-evaluation fires no rule, THE SYSTEM SHALL record a SEM_MUDANCA decision and keep the current stage.`
- `IF TechLab AI orchestration is unavailable, times out, or the circuit is open, THEN THE SYSTEM SHALL decide with deterministic rules only and record assist_ia=INDISPONIVEL, never blocking the decision.`
- `WHEN orchestration returns within the timeout, THE SYSTEM SHALL fold the recommendation into the decision and record assist_ia=USADO with the suggestion and confidence.`
- `IF a mandatory guard rule applies, THEN THE SYSTEM SHALL honor the rule over any AI recommendation and record assist_ia=IGNORADO.`
- `THE SYSTEM SHALL evaluate condicao as a pure function of snapshot_entrada so the same snapshot and the same rule version always yield the same decision.`
- `WHEN the target stage is terminal, THE SYSTEM SHALL set the enrolment to CONCLUIDA and emit journey-os.jornada.concluida.`
- `THE SYSTEM SHALL record snapshot_entrada and the fired regra_id on every decision for auditability.`
- `THE SYSTEM SHALL never have JRNY execute a channel or sales action — it SHALL only decide and emit events for COMM/SALE.`
