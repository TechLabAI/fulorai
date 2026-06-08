# 02 — Architecture Blueprint — ASST (Asset Hub)

> Como ASST se posiciona no ecossistema Journey OS: fronteiras, atores, fluxos e camadas.

## 1. System Boundary

ASST (`asst-service`, `com.journeyos.asst`) é dono do **ciclo de vida do asset** dentro de um
workspace (`empresa`): criação, versionamento, aprovação, publicação, composição assistida e
indexação para busca. A fronteira **inclui**:

- O agregado `Asset` e suas `VersaoAsset` (versões imutáveis).
- A `Aprovacao` e a máquina de estados de publicação.
- A orquestração do Asset Studio (chamada à TechLab AI `document_composition`).
- A projeção de busca/Asset Intelligence no índice Elastic `assets`.

A fronteira **exclui** (pertence a outros donos):

- Identidade, RBAC, contexto de tenant → **WRKS** (ASST apenas consome `AccessDecision`/JWT).
- Provisionamento de schema `emp_<slug>` → **MIG/WRKS**.
- Entrega/envio de mensagens que usam o asset → **COMM**.
- Capacidade de IA (modelos, prompts, providers) → **TechLab AI** (consumida via HTTP).

## 2. External Actors and Systems

| Ator/Sistema | Tipo | Interação com ASST |
|---|---|---|
| **HEAD_GROWTH / INFOPRODUTOR / SDR** | humano (via GWY → FE) | CRUD de assets, Asset Studio, submissão/aprovação, busca. |
| **WRKS** | serviço (sync) | Valida JWT (JWKS) + `POST /access/evaluate` para autorização `asst.*`. |
| **TechLab AI** | serviço externo (sync/async HTTP) | `document_composition` (Asset Studio) + classificação (Asset Intelligence). |
| **Elasticsearch** | infra (sync, direct java client) | Índice `assets` (dimension) — busca + projeção de Asset Intelligence. |
| **PostgreSQL** (`emp_<slug>`) | infra | Fonte da verdade dos assets/versões/aprovações do tenant. |
| **Kafka / AWS MSK** | infra (async) | Produz/consome eventos `journey-os.*`. |
| **COMM / JRNY / SALE** | serviço (sync + async) | Consomem assets publicados (Feign `AssetQueryClient` + evento `asset.versao.publicada`). |
| **MIG** | serviço | Prepara o schema do tenant (precondição). |

## 3. End-to-End Flows

### Golden path — *Compor → submeter → aprovar → publicar*

```
Marina (HEAD_GROWTH)
  → POST /api/v1/assets                      (cria asset RASCUNHO, tipo=EMAIL)
  → POST /api/v1/assets/{id}/studio/compose  (Asset Studio)
        → ASST chama TechLab AI document_composition (brief + contexto empresa)
        → cria VersaoAsset v1 (RASCUNHO) com conteúdo composto
        → (Asset Intelligence) classifica/tagueia → indexa em Elastic `assets`
  → POST /api/v1/assets/{id}/submit          (RASCUNHO → EM_REVISAO)
Rafael (INFOPRODUTOR)
  → POST /api/v1/assets/{id}/approve         (EM_REVISAO → APROVADO; grava Aprovacao)
  → POST /api/v1/assets/{id}/publish         (APROVADO → PUBLICADO; v1 vira versão vigente)
        → emite journey-os.asset.versao.publicada
        → reindexa Elastic `assets` (estado=PUBLICADO)
COMM/JRNY/SALE
  → consomem o evento e/ou GET /api/v1/assets/{id}/published (Feign AssetQueryClient)
```

### Fluxos alternativos

- **Rejeição:** `POST /approve` com decisão negativa → `EM_REVISAO → REJEITADO`; emite `asset.rejeitado`; autor revisa e cria nova versão (`RASCUNHO`).
- **Composição manual (sem IA):** Marina cria/edita `VersaoAsset` diretamente (sem Asset Studio); demais transições idênticas.
- **TechLab AI indisponível:** Asset Studio retorna `503`/ProblemDetail de degradação; CRUD, submissão, aprovação e publicação **não** são afetados (ver `ADR-003`).
- **Nova versão de asset publicado:** publicar v2 não apaga v1; v1 fica `PUBLICADO` histórico, v2 vira vigente (proveniência preservada — `ADR-005`).

## 4. Internal Boundaries (camadas hexagonais)

```
api/            controllers REST (/api/v1/assets/**, /asset-studio), DTO records, @RestControllerAdvice
application/    use cases (@Service, @Transactional): CriarAsset, ComporNoStudio, SubmeterAsset,
                AprovarAsset, PublicarAsset, BuscarAssets; ports in/out
domain/         Asset, VersaoAsset, Aprovacao, EstadoAsset (state machine), TipoAsset — POJO puro;
                domain services (regra de transição, invariantes de versão) — zero Spring/JPA
infrastructure/ persistence (JPA emp_<slug>), clients (Feign WRKS + client TechLab AI),
                messaging (producer/consumer Kafka), search (Elastic adapter `assets`),
                security (EmpresaContextHolder, filtros JWT), config (DomainServiceConfig)
```

Regras ArchUnit RULE-01..09 (ver `ADR-001` e `hexagonal-patterns.md`).

## 5. Cross-cutting Concerns

- **Security / multi-tenancy:** todo request carrega JWT (validado contra JWKS de WRKS); `EmpresaContextHolder.require()` fixa o `emp_<slug>`; autorização por permissões `asst.<recurso>.<acao>` via `AccessDecision` (cache curto, invalidado por `modelo.acesso.alterado`).
- **Observability:** MDC com `correlationId` + `empresaId`; logs estruturados (SLF4J/Lombok); métricas de latência do Asset Studio (chamada TechLab AI) e da indexação Elastic.
- **Resiliência:** chamadas à TechLab AI com timeout + circuit breaker (Resilience4j) + fallback graceful; eventos com outbox/idempotência (ver SPEC-05).
- **LGPD:** assets podem conter dados pessoais (ex.: nomes em scripts) → retenção/arquivamento por tenant; exclusão lógica preserva trilha de versões para auditoria.
- **Idempotência:** publicar/aprovar são idempotentes por versão+estado; composição do Studio usa chave de requisição para evitar duplicação.

---

## Referências

- `01-architectural-vision.md` · `03-initial-domain-framing.md` · `04-backend-architecture-direction.md`
- `docs/architecture/backend/standards/hexagonal-patterns.md` · `platform-patterns.md`
- `docs/architecture/integrations/techlab-ai-integration.md` · `elastic-data-contract.md`
