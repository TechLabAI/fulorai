# ADR-012 — CQRS-light (commands/queries/policies/permissions) sem event sourcing completo

> **Data:** 2026-06-04
> **Status:** draft (BA)
> **Decisor:** Arquiteto (Danilo Amaral) — pendente de promoção

---

## Contexto

A Application Layer do Journey OS (Framing §5.2) é descrita como **CQRS-light**:
commands, queries, policies e permissions, sobre a arquitetura hexagonal
(ADR-004). O produto tem uma assimetria natural: a **escrita** passa por
invariantes de domínio e emite eventos (event-first, ADR-008), enquanto a
**leitura** é servida por múltiplas projeções (PostgreSQL canônico para leitura
forte — ADR-006; Elasticsearch para busca/analytics — ADR-007). RBAC granular
(View/Create/Edit/Approve/Publish/Delete/Manage por módulo — Framing §10.3) e
policies por command são requisitos transversais.

A decisão técnica: **qual estilo de organização da camada de aplicação** —
CRUD simples, CQRS-light (separar commands de queries sem event store como fonte
de verdade) ou event sourcing pleno (estado reconstruído de um event log
canônico)?

---

## Opções consideradas

### Opção A — CQRS-light (DECIDIDA)
- **Vantagens:**
  - Separa **commands** (escrita: validação, invariantes, policies, permissions,
    emite eventos) de **queries** (leitura: serve do canônico ou de projeções
    Elastic) — encaixa na assimetria escrita/leitura do produto.
  - PostgreSQL continua a fonte de verdade (ADR-006); eventos via outbox (ADR-008)
    alimentam projeções — **sem** exigir event store como verdade.
  - Policies/permissions por command dão lugar natural ao RBAC granular.
- **Desvantagens:**
  - Mais estrutura que CRUD (command/query handlers).
  - Disciplina para não deixar leitura "vazar" para o caminho de escrita.
- **Custo:** médio.

### Opção B — CRUD simples (services genéricos)
- **Vantagens:**
  - Menos código; rápido de começar.
- **Desvantagens:**
  - Mistura leitura e escrita; difícil aplicar policies/permissions por operação
    de forma consistente; não modela bem a fan-out de projeções (Elastic/eventos).
  - Tende a acoplar queries pesadas ao modelo transacional.
- **Custo:** baixo inicial, dívida ao crescer.

### Opção C — Event sourcing pleno
- **Vantagens:**
  - Histórico completo como fonte de verdade; auditoria total; replay nativo.
- **Desvantagens:**
  - Complexidade alta (versionamento de eventos, snapshots, projeções
    obrigatórias para tudo) desproporcional ao MVP e ao time enxuto (ORG-001).
  - Conflita com "PostgreSQL é o system of record" (ADR-006): a verdade passaria
    a ser o event log, não as tabelas canônicas.
- **Custo:** alto; over-engineering para o MVP.

---

## Decisão

Escolhida: **Opção A — CQRS-light**. Commands e queries separados; PostgreSQL é a
fonte de verdade (não há event store canônico); eventos (ADR-008) alimentam
projeções de leitura (Elastic, ADR-007). Policies e permissions (RBAC) aplicadas
no caminho de command.

---

## Justificativa

1. **Reflete a assimetria real do produto.** Escrita com invariantes + eventos;
   leitura de múltiplas projeções (canônico forte e Elastic eventual). CQRS-light
   nomeia essa separação sem o custo do event sourcing pleno.

2. **Compatível com ADR-006 e ADR-008.** A verdade fica no Postgres (ADR-006); o
   outbox/eventos (ADR-008) já existem para projeções — CQRS-light usa esse fluxo
   sem transformar o event log em fonte canônica (o que ES pleno exigiria e
   conflitaria com TECH-003/ADR-006).

3. **RBAC granular tem lar natural.** Policies/permissions por command (Framing
   §10.3) são limpos quando a escrita é explicitamente modelada como command,
   não diluída em CRUD.

4. **Proporcional ao MVP e ao time (ORG-001, LBC §7/§12).** Entrega a separação
   útil sem a complexidade de snapshots/versionamento de ES pleno.

---

## Trade-offs aceitos

- **Perdemos:** simplicidade do CRUD. Justificativa: CRUD não modela bem
  policies por operação nem a fan-out de projeções do produto.
- **Perdemos:** o histórico-como-verdade e replay total do ES pleno.
  Justificativa: o EventStore/outbox (ADR-008) já dá replay de projeções
  suficiente; ES pleno seria over-engineering e conflitaria com ADR-006.
- **Perdemos:** modelos de leitura/escrita unificados. Justificativa: a separação
  é o ponto — vale a disciplina extra.

---

## Como reverter se a decisão se mostrar errada

**Para CRUD (simplificar):** fundir command/query handlers em services; manter
RBAC. **Custo:** baixo-médio, perde clareza de policies.

**Para event sourcing pleno (evoluir):** promover o EventStore (ADR-008) a fonte
de verdade por agregado, introduzir snapshots e projeções obrigatórias. **Custo:**
alto, decisão deliberada por agregado específico que exigir auditoria total —
provavelmente só alguns (ex.: routing decisions, attribution), não o sistema todo.
Como ainda **não há código de produção** (Estágio 0), o nível de CQRS pode ser
ajustado agora a custo baixo.

---

## Sinais que indicariam que está errada

- Boilerplate de command/query handlers virando ônus sem benefício percebido
  (sinal de que CRUD bastaria para parte dos módulos).
- Requisito de auditoria/replay total em agregados específicos que CQRS-light não
  atende — gatilho para event sourcing **localizado** naquele agregado.
- Divergência frequente entre projeções e canônico causando bugs de leitura —
  sinal de problema na malha de eventos (ADR-008), não necessariamente no CQRS.

---

## Consequências

- **Em código:** Application Layer com command handlers (validação, policies,
  permissions, emissão de eventos) e query handlers (leem canônico ou Elastic);
  sobre hexagonal (ADR-004).
- **Em dados:** Postgres = verdade (ADR-006); projeções via eventos (ADR-008) em
  Elastic (ADR-007).
- **Em segurança:** RBAC por command/módulo (Framing §10.3), escopado por tenant
  (ADR-003).

---

## Referências

- LBC §7 (MVP enxuto), §12 (evitar complexidade/custo prematuros)
- Framing §5.2 (Application Layer CQRS-light), §10.3 (RBAC granular)
- Constraints: TECH-001 (Spring/hexagonal), ORG-001
- ADRs relacionados: ADR-004 (hexagonal), ADR-006 (Postgres = verdade), ADR-008
  (eventos/outbox alimentam projeções), ADR-007 (projeções de leitura), ADR-003 (RBAC por tenant)
