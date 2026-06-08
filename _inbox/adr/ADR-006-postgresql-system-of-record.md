# ADR-006 — PostgreSQL como system of record + pgVector para embeddings

> **Data:** 2026-06-04
> **Status:** draft (BA)
> **Decisor:** Arquiteto (Danilo Amaral) — pendente de promoção

---

## Contexto

O Journey OS precisa de um banco canônico transacional (system of record) para
todo dado de negócio: Workspace/Identity, Lead/Score, Journey/Routing, Asset,
Communication, Sales/Revenue, CRM, permissões e o EventStore/outbox (Framing
§7). O princípio inviolável §2.2 / TECH-003 define que **PostgreSQL é a verdade
canônica** e o **Elasticsearch nunca é banco primário** (recebe só projeções —
ADR-007).

Além disso, a IA (ADR-002) faz RAG híbrido que precisa de **embeddings**
armazenados junto ao registro (AssetVersion, KnowledgeNode, respostas de survey,
notas de CRM — Framing §9.2). A decisão técnica: **qual banco relacional
canônico e como guardar embeddings?**

O PRD original (§10) propunha **Supabase** (Postgres gerenciado + auth + storage).
Descartado (EXC-001) em favor do PostgreSQL alinhado ao framework. A decisão
inclui o eixo **managed vs self-managed**.

---

## Opções consideradas

### Opção A — PostgreSQL (self/managed neutro) + extensão pgVector (DECIDIDA)
- **Vantagens:**
  - Cumpre TECH-003 e o default do framework (schema-per-empresa via ADR-003).
  - Transacional robusto para domínios densos + outbox transacional (ADR-008)
    na **mesma transação** do dado canônico (garantia event-first do §2.1).
  - **pgVector guarda embeddings junto ao registro** — RAG sem mover dado para
    outro store; um só backup, um só modelo de consistência.
  - Portável entre cloud providers (RDS, Cloud SQL, self-hosted) — sem lock-in
    de vendor.
- **Desvantagens:**
  - pgVector escala a busca vetorial até certo volume; índices ANN (HNSW) pesados
    podem exigir tuning em escala alta.
  - Operar Postgres você mesmo exige expertise de DBA (mitigável com managed).
- **Custo:** baixo a médio.

### Opção B — Supabase — stack do PRD §10
- **Vantagens:**
  - Postgres gerenciado + auth + storage + pgvector embutido; velocidade de setup.
- **Desvantagens:**
  - Lock-in ao vendor (auth/RLS/edge functions específicos) que não se encaixam
    no schema-per-empresa do framework (ADR-003) nem no backend Java (ADR-001).
  - Multi-tenancy do Journey OS é schema-per-empresa, não o modelo RLS+auth que o
    Supabase favorece.
  - Viola TECH-003/EXC-001 (fora do framework).
- **Custo:** baixo setup, alto custo estratégico de lock-in.

### Opção C — PostgreSQL canônico + store vetorial dedicado (ex.: Qdrant/Weaviate)
- **Vantagens:**
  - Busca vetorial em escala muito alta com tuning especializado.
- **Desvantagens:**
  - Mais um datastore para operar (time enxuto, ORG-001) e sincronizar com o
    canônico — risco de divergência embedding↔registro.
  - Prematuro para o volume do MVP/piloto.
- **Custo:** alto operacional, prematuro.

---

## Decisão

Escolhida: **Opção A — PostgreSQL canônico + pgVector**, **gerenciado na AWS
(RDS/Aurora)** (D1, sponsor 2026-06-04). Com time pleno sem DBA/SRE dedicado
(ORG-001), o serviço gerenciado cuida de backup/HA/upgrades, dentro do envelope
da FIN-001 (TECH-007). A escolha do motor (Postgres+pgVector) independe da
hospedagem e preserva portabilidade sem lock-in; a alternativa self-hosted em K8s
foi considerada e descartada (risco operacional).

---

## Justificativa

1. **Outbox transacional exige o canônico relacional (event-first, §2.1).** Gravar
   o evento na **mesma transação** do dado de negócio só é confiável num RDBMS
   ACID; Postgres é a base do padrão outbox→Kafka (ADR-008).

2. **RAG simples e consistente com pgVector.** Manter embeddings junto ao registro
   (Framing §9.2) evita um segundo datastore e o risco de divergência — crítico
   para que o Copilot cite a fonte correta (LBC §8). O retrieval híbrido combina
   pgVector (preciso, junto ao dado) com Elastic (escala/filtros, ADR-007).

3. **Sem lock-in de vendor (vs Supabase).** Portabilidade entre clouds preserva
   independência estratégica (LBC §2.3) e encaixa no schema-per-empresa (ADR-003).

4. **Cumpre TECH-003** e o default do framework.

---

## Trade-offs aceitos

- **Perdemos:** conveniência all-in-one do Supabase (auth/storage prontos).
  Justificativa: lock-in e desencaixe com o framework custam mais que o setup
  manual de auth (RBAC próprio, WRKS) e storage (object storage à parte).
- **Perdemos:** busca vetorial de altíssima escala de um store dedicado.
  Justificativa: pgVector cobre o volume do MVP/piloto; store dedicado fica como
  evolução se o volume exigir.
- **Perdemos:** simplicidade de não operar Postgres. Justificativa: mitigável com
  Postgres gerenciado, sem trocar o motor.

---

## Como reverter se a decisão se mostrar errada

**Trocar a busca vetorial (manter Postgres canônico):** introduzir store vetorial
dedicado, sincronizado por consumer (mesmo padrão do indexer Elastic, ADR-007).
**Custo:** dias a semanas; baixo risco porque o canônico não muda.

**Trocar o canônico (improvável):** migrar de Postgres para outro RDBMS exige
migração de dados + reescrita do schema resolver e do outbox. **Custo:** alto.
Como ainda **não há dados de produção** (Estágio 0), reverter hoje é barato.

---

## Sinais que indicariam que está errada

- Latência/recall da busca vetorial em pgVector inaceitável para o Copilot mesmo
  após tuning de índice ANN, de forma consistente.
- Volume de embeddings/leads tornando o Postgres único gargalo de I/O acima do
  orçamento de infra (FIN-001).
- Necessidade de features de busca vetorial (re-ranking nativo, filtros híbridos
  avançados) que só um store dedicado oferece e que viram requisito frequente.

---

## Consequências

- **Em código:** repositories via adapters (ADR-004); outbox na mesma transação
  (ADR-008); embeddings em colunas pgVector junto a AssetVersion/KnowledgeNode/etc.
- **Em multi-tenancy:** schema-per-empresa (ADR-003) sobre este Postgres.
- **Em IA:** RAG híbrido lê pgVector + Elastic, filtrado por workspace (ADR-002).

---

## TODOs

- ~~`TODO[arquiteto]: managed vs self-hosted`~~ — **RESOLVIDO (D1, sponsor 2026-06-04):**
  PostgreSQL gerenciado na AWS (RDS/Aurora). Self-hosted em K8s considerado e descartado.
- `TODO[arquiteto]: escolher RDS vs Aurora e dimensionar instância/HA (Multi-AZ)
  dentro do teto da FIN-001; confirmar versão com suporte a pgVector.`

---

## Referências

- LBC §2.3 (independência estratégica), §8 (RAG/Copilot)
- Framing §2.2 (Postgres canônico), §7 (núcleos de dados), §9.2 (RAG/pgVector), §11 (stack)
- Constraints: TECH-003, EXC-001, FIN-001
- ADRs relacionados: ADR-003 (schema-per-empresa), ADR-007 (Elastic = projeção, não primário),
  ADR-008 (outbox transacional no Postgres), ADR-002 (RAG híbrido)
