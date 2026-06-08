# ADR-003 — Multi-tenancy: schema-per-empresa em PostgreSQL único

> **Data:** 2026-06-04
> **Status:** draft (BA)
> **Decisor:** Sponsor (Danielle Amaral) decidiu o modo em 2026-06-04; arquiteto (Danilo Amaral) fecha o ADR — pendente de promoção

---

## Contexto

O Journey OS é SaaS B2B multi-tenant onde **Workspace** é a entidade raiz de
isolamento (Framing §2.3/§10; TECH-004). Cada cliente (infoprodutor) opera
isoladamente: leads (PII — REG-001/LGPD), jornadas, assets, CRM, receita e
índices Elastic não podem vazar entre workspaces. Isolamento forte, backup por
cliente, exclusão por cliente (LGPD) e provisionamento automatizável são
requisitos.

O PRD original desenhou **row-based**: `workspace_id` em toda tabela + RLS
PostgreSQL. O framework `techlab-architecture` adota por padrão
**schema-per-empresa** (gerado por `new-project.py`, schema resolver Hibernate).
A decisão técnica é: **como isolar dados entre workspaces no Postgres?**
Decidido por **Danielle Amaral (sponsor) em 2026-06-04: schema-per-empresa**,
com `globalSchema = journeyos_global`.

Particularidade do Journey OS: o mercado-alvo são **infoprodutores** —
potencialmente **alta cardinalidade de tenants** se o produto escalar para
self-service, diferente de um SaaS enterprise com dezenas de clientes. Isso é o
trade-off central a documentar.

---

## Opções consideradas

### Opção A — Schema-per-empresa em PostgreSQL único (DECIDIDA)
- **Vantagens:**
  - Isolamento lógico forte (schema por Workspace; `search_path` por request).
  - Default do framework — gerador, schema resolver e templates já assumem isso
    (cumpre TECH-004 sem reescrever ferramental).
  - Exclusão LGPD por cliente trivial e auditável (`DROP SCHEMA ws_X CASCADE`).
  - Backup seletivo (`pg_dump --schema=ws_X`); pool de conexões compartilhado.
  - Provisionamento de cliente = `CREATE SCHEMA + run migrations`.
- **Desvantagens:**
  - **Migrations precisam rodar em cada schema** — N schemas = N execuções.
  - Erro de propagação de `search_path` pode vazar dados (mitigável com testes).
  - **Alta cardinalidade de tenants** (muitos infoprodutores) gera muitos
    schemas: limite prático do Postgres (~milhares) e custo de VACUUM/REINDEX/
    catálogo crescente.
- **Custo:** médio operacional; risco específico na alta cardinalidade.

### Opção B — Row-based (`workspace_id` + RLS) — desenho original do PRD
- **Vantagens:**
  - Migrations rodam uma única vez.
  - Escala melhor para altíssima cardinalidade de tenants (sem proliferação de
    schemas).
  - Analytics cross-tenant (uso interno da plataforma) trivial.
- **Desvantagens:**
  - Vazamento se uma policy RLS ou filtro falhar — risco crítico em SaaS.
  - Toda query depende de RLS/`workspace_id` correto (disciplina + índices
    começando por `workspace_id`).
  - Backup/exclusão LGPD por cliente complexos (filtrar N tabelas).
  - **Fora do padrão do framework** — exigiria adaptar gerador e schema resolver.
- **Custo:** baixo de migration, alto de risco/adaptação de ferramental.

### Opção C — Database-per-tenant
- **Vantagens:**
  - Isolamento físico máximo; tuning/backup independentes.
- **Desvantagens:**
  - Pool e custo de cloud por database escalam mal — inviável com muitos
    infoprodutores.
  - Provisionamento e migrations pesados por cliente.
- **Custo:** alto operacional; pior cenário para a cardinalidade esperada.

---

## Decisão

Escolhida: **Opção A — schema-per-empresa em PostgreSQL único**, decidida pelo
sponsor em 2026-06-04. `globalSchema = journeyos_global`.

`workspace_id` (do PRD) **não some**: deixa de ser filtro row-based e passa a ser
o **discriminador de tenant que mapeia Workspace → schema**. Nos índices Elastic
(ADR-007), o discriminador de tenant continua **obrigatório em todo documento**
(alias/índice por tenant quando aplicável), pois o Elastic não tem schemas.

---

## Justificativa

1. **Isolamento forte é requisito de sobrevivência do SaaS.** Vazamento entre
   workspaces é risco grave (LBC §12; REG-001/LGPD). Schema-per-empresa é
   "harder to fuck up" que RLS row-based: a separação é estrutural, não
   dependente de toda query carregar o filtro certo.

2. **Alinhamento com o framework (TECH-004).** O `new-project.py` gera o schema
   resolver e o `journeyos_global`; adotar o default evita reescrever a malha de
   multi-tenancy num projeto com time enxuto (ORG-001).

3. **LGPD por cliente é operação de primeira classe.** `DROP SCHEMA ws_X
   CASCADE` resolve direito ao esquecimento de forma auditável — diferente de
   limpar N tabelas filtradas no modelo row-based.

O trade-off de alta cardinalidade é **conhecido e aceito** com mitigação
(automação de migrations por schema; reavaliar estratégia se a cardinalidade
explodir). É consequência reversível registrada nos sinais abaixo.

---

## Trade-offs aceitos

- **Perdemos:** migration única do modelo row-based. Justificativa: automação de
  migrations por schema (script que itera schemas) mitiga; isolamento vale o custo.
- **Perdemos:** escalabilidade trivial para altíssima cardinalidade de tenants.
  Justificativa: no MVP/piloto (1 infoprodutor → poucos), a cardinalidade é
  baixa; reavaliação fica registrada para o cenário self-service.
- **Perdemos:** analytics cross-tenant simples (uso interno). Justificativa: não é
  caso de uso do produto; quando preciso, há views em `journeyos_global` ou DW.

---

## Como reverter se a decisão se mostrar errada

**Para row-based (Opção B), se a cardinalidade de tenants inviabilizar schemas:**
1. Criar tabelas globais com `workspace_id` + policies RLS.
2. Migrar dados de cada schema para as tabelas globais (`INSERT ... SELECT`,
   iterando schemas).
3. Refatorar repositories para discriminador + RLS; ajustar schema resolver.
4. **Custo:** alto e arriscado, com janela de manutenção — semanas, proporcional
   ao nº de schemas e tabelas. Como ainda **não há dados de produção** (Estágio
   0), reverter hoje é barato; o custo cresce a cada cliente onboardado.

**Para database-per-tenant (Opção C):** `pg_dump --schema` → restore em novo DB
por cliente; ~1-2 dias por tenant. Improvável dado o custo de cloud.

---

## Sinais que indicariam que está errada

- Número de schemas se aproximando do limite prático do Postgres ou tornando
  catálogo/migrations lentos (ex.: rodada de migrations levando horas; VACUUM/
  REINDEX dominando janela de manutenção).
- Modelo de negócio virar self-service em massa (milhares de workspaces) — a
  cardinalidade inverte o trade-off a favor de row-based.
- Custo de manter pool (pgbouncer) e provisionamento por schema crescer
  desproporcionalmente.

---

## Consequências

- **Em código:** `WorkspaceContextHolder` (ou equivalente) em filter de cada
  request; Hibernate schema resolver define `search_path`; headers Kafka
  (ADR-008) propagam o tenant; `journeyos_global` guarda catálogo de workspaces,
  billing e config de plataforma.
- **Em Elastic (ADR-007):** discriminador de tenant obrigatório em todo
  documento + filtro por workspace em toda query/RAG (ADR-002); document-level
  security para planos enterprise.
- **Em operações:** novo cliente = `provision-workspace.sql`; backup seletivo
  `pg_dump --schema`; LGPD = `DROP SCHEMA ws_X CASCADE` + remoção em
  `journeyos_global`.

---

## Referências

- LBC §2.3 (independência/isolamento por Workspace), §12 (risco de vazamento)
- Framing §2.3 (multi-tenant nativo), §10 (estratégia multi-tenant, decisão do sponsor)
- Constraints: TECH-004, REG-001 (LGPD)
- ADRs relacionados: ADR-001 (Hibernate/JVM), ADR-004 (persistence via adapter),
  ADR-007 (discriminador de tenant no Elastic), ADR-008 (tenant em headers Kafka)
