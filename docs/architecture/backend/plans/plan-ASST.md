# Plano -- ASST (Asset Hub)

## Status das prioridades
- P1 -- pendente
- P2 -- pendente
- P3 -- pendente
- P4 -- pendente
- P5 -- pendente
- P6 -- pendente
- P7 -- pendente
- P8 -- pendente

## 0. Leitura executiva

### Papel do serviço (01-architectural-vision.md)
ASST é o repositório único de ativos de conteúdo do workspace: catalogação, **versionamento
imutável**, **workflow de aprovação** e **Asset Studio** (composição assistida por IA via TechLab
AI `document_composition`). Assets publicados são consumidos por COMM/JRNY/SALE. Opera somente no
schema `emp_<slug>` e nunca chama provider de IA direto.

### MVP scope (01)
Asset CRUD + catálogo; versionamento imutável; approval workflow (rascunho→revisão→aprovado→
publicado); Asset Studio (document_composition); Asset Intelligence (tagging + índice Elastic
`assets`); busca/listagem; consumo cross-módulo (Feign + evento).

### Diagnóstico inicial (gaps — 06)
- Contrato TechLab AI `document_composition` ainda placeholder (P3 bloqueado) → coupling point marcado.
- Schema `conteudo` jsonb por `tipo_asset` a detalhar no implement.
- Permissões `asst.*` a confirmar no RBAC global.
- Binários por URL (object storage S3 é pós-MVP).

## 1. Estratégia geral

### Objetivo macro
Entregar o golden path *criar → compor (Studio) → submeter → aprovar → publicar* com
versionamento imutável e proveniência, expondo assets publicados à plataforma; depois reforçar
integrações (IA/Elastic), segurança, mensageria e BDD.

### Ordem das prioridades

| P | Título | Motivo |
|---|---|---|
| P1 | Scaffold + domínio + API CRUD | Base executável + máquina de estados testável |
| P2 | Golden path (versão→aprovação→publicação) | Evento-âncora `asset.versao.publicada` |
| P3 | Persistência + migrations | Fonte da verdade no `emp_<slug>` |
| P4 | Integrações (TechLab AI + Elastic) | Asset Studio + Asset Intelligence + busca |
| P5 | Security + multi-tenancy + idempotência | Autorização `asst.*`, tenant guard, replays |
| P6 | Messaging | Eventos (outbox) + consumo idempotente + AssetQueryClient |
| P7 | Observability + health | Actuator, métricas Studio/index, MDC |
| P8 | BDD end-to-end | Gate D-218 (toda SHALL → cenário) |

## 2. Plano por prioridade

### Prioridade 1 -- Scaffold + domínio + API CRUD
Status: pendente
#### Objetivo / Resultado esperado
Serviço sobe (Eureka/Actuator), domínio puro com state machine, CRUD de asset com DTO/ProblemDetail.
#### Issues vinculadas
- ASST-001, ASST-002, ASST-003, INT-ASST-001
#### Specs cobertas
- SPEC-01, SPEC-02, SPEC-07
#### Sequência de execução
- Fase 1: bootstrap (ASST-001 + INT-ASST-001) · Fase 2: domínio (ASST-002) · Fase 3: API CRUD (ASST-003)
#### Critérios de aceite
- build + architectureCheck PASS; `POST /` cria asset RASCUNHO; transição inválida lança erro de domínio.
#### Riscos
- Acoplamento acidental domínio↔Spring (mitigado por ArchUnit).
#### Instrução para implementador
- `/be-implement ASST P1`. Domínio sem Spring/JPA (RULE-01/02); controller retorna DTO.

### Prioridade 2 -- Golden path (versão → aprovação → publicação)
Status: pendente
#### Objetivo / Resultado esperado
Versionamento imutável + submit/approve/reject + publish (versão vigente + evento-âncora).
#### Issues vinculadas
- ASST-004, ASST-005, ASST-006
#### Specs cobertas
- SPEC-02, SPEC-01, SPEC-09
#### Sequência de execução
- Fase 1: versão (ASST-004) · Fase 2: submit/approve (ASST-005) · Fase 3: publish + evento (ASST-006)
#### Critérios de aceite
- Transições inválidas → 409; `asset.versao.publicada` emitido; versões anteriores preservadas.
#### Riscos
- Estado corrompido por transição fora da máquina (mitigado: só pelo agregado raiz).
#### Instrução para implementador
- `/be-implement ASST P2`. Versão imutável (ADR-005); evento via outbox.

### Prioridade 3 -- Persistência + migrations
Status: pendente
#### Objetivo / Resultado esperado
DDL no `emp_<slug>` (sem `empresa_id`) + adapters JPA respeitando isolamento de schema.
#### Issues vinculadas
- ASST-007, ASST-008
#### Specs cobertas
- SPEC-04, SPEC-06
#### Sequência de execução
- Fase 1: migrations (ASST-007) · Fase 2: JPA/adapters (ASST-008)
#### Critérios de aceite
- `ddl-auto=validate` passa; round-trip via Testcontainers; sem entity na API.
#### Riscos
- Vazamento cross-tenant (mitigado: search_path + sem `empresa_id`).
#### Instrução para implementador
- `/be-implement ASST P3`. Migrations em `journey-os-migrations` (`db/migration/empresa/`).

### Prioridade 4 -- Integrações (TechLab AI + Elastic)
Status: pendente
#### Objetivo / Resultado esperado
Asset Studio (document_composition) + Asset Intelligence + busca Elastic, resilientes.
#### Issues vinculadas
- ASST-009, ASST-010, ASST-011, INT-ASST-003, INT-ASST-004
#### Specs cobertas
- SPEC-03, SPEC-10
#### Sequência de execução
- Fase 1: cliente TechLab AI (INT-ASST-003) → Studio (ASST-009) · Fase 2: Intelligence (ASST-010) · Fase 3: Elastic (INT-ASST-004 → ASST-011)
#### Critérios de aceite
- Studio cria versão IA com proveniência; IA down → 503 sem afetar CRUD; busca cai para PostgreSQL se Elastic down.
#### Riscos
- `openapi.json` placeholder (P3) → DTOs gerados quando o SHA for pinado.
#### Instrução para implementador
- `/be-implement ASST P4`. Nunca chamar provider de IA direto; DTOs gerados de `openapi.json`.

### Prioridade 5 -- Security + multi-tenancy + idempotência
Status: pendente
#### Objetivo / Resultado esperado
JWT + AccessDecision (`asst.*`) + tenant guard; composição/publicação idempotentes; concorrência otimista.
#### Issues vinculadas
- ASST-012, ASST-013, INT-ASST-002
#### Specs cobertas
- SPEC-06, SPEC-05
#### Sequência de execução
- Fase 1: AccessDecision (INT-ASST-002) → segurança (ASST-012) · Fase 2: idempotência/concorrência (ASST-013)
#### Critérios de aceite
- 401/403 corretos; cross-tenant impossível; `Idempotency-Key` → 1 versão; publish idempotente.
#### Riscos
- Cache de AccessDecision desatualizado (mitigado: invalidação por `modelo.acesso.alterado`).
#### Instrução para implementador
- `/be-implement ASST P5`. `@Transactional` só em application.service (RULE-03).

### Prioridade 6 -- Messaging
Status: pendente
#### Objetivo / Resultado esperado
Producers (outbox) + consumers idempotentes + contrato AssetQueryClient para consumidores.
#### Issues vinculadas
- ASST-014, INT-ASST-005, INT-ASST-006
#### Specs cobertas
- SPEC-09, SPEC-01
#### Sequência de execução
- Fase 1: Kafka config (INT-ASST-005) → producers/consumers (ASST-014) · Fase 2: AssetQueryClient (INT-ASST-006)
#### Critérios de aceite
- Rollback não publica; reentrega → no-op; `/published` só versão vigente.
#### Riscos
- Ghost events (mitigado: outbox).
#### Instrução para implementador
- `/be-implement ASST P6`. Consumer sem chamada Feign síncrona.

### Prioridade 7 -- Observability + health
Status: pendente
#### Objetivo / Resultado esperado
Actuator + métricas (Studio/index) + MDC; readiness UP mesmo com IA/Elastic degradados.
#### Issues vinculadas
- ASST-015
#### Specs cobertas
- SPEC-07
#### Critérios de aceite
- `/actuator/health` liveness/readiness; logs com `correlationId`/`empresaId`.
#### Instrução para implementador
- `/be-implement ASST P7`. `@Slf4j`, nunca `System.out`.

### Prioridade 8 -- BDD end-to-end
Status: pendente
#### Objetivo / Resultado esperado
Cenários Cucumber executáveis cobrindo as 125 cláusulas SHALL (gate D-218).
#### Issues vinculadas
- ASST-016
#### Specs cobertas
- SPEC-08 (+ todas)
#### Critérios de aceite
- `*CucumberIT*` executa os 3 features; ≥1 cenário por SHALL; TechLab AI/WRKS stubados.
#### Instrução para implementador
- `/be-implement ASST P8`. Testcontainers PostgreSQL com schema migrado.

## 3. Dependências externas
- **WRKS** (AccessDecision/JWKS) — runtime. **MIG** (schema `emp_<slug>`). **TechLab AI**
  (`document_composition`, P3 placeholder). **Elasticsearch** (`assets`). **Kafka/AWS MSK**. **REG/GWY**.

## 4. Restrições arquiteturais
- ArchUnit RULE-01..09 (CLAUDE.md) — bloqueante.
- Camadas hexagonais (api/application/domain/infrastructure).
- `@Transactional` somente em `application.service`.
- Domínio sem Spring/JPA; controller nunca retorna `@Entity`.
- Nunca chamar provider de IA direto (sempre via TechLab AI HTTP).
- Tabelas operacionais sem `empresa_id` (schema isola).

## 5. Referências
- `docs/architecture/backend/services/asst-service/` (vision 01..06, ADRs, contracts, specs, diagrams)
- `docs/architecture/backend/issues/ASST-001..016.md`, `INT-ASST-001..006.md`, `issues_map-ASST.md`
- `docs/architecture/backend/services/asst-service/generator-config.yml`
