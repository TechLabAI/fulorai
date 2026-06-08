# 02 — Architecture Blueprint — JRNY (Journey & Routing)

> Como JRNY se posiciona no ecossistema Journey OS: fronteiras, atores, fluxos e camadas.

## 1. System Boundary

JRNY (`jrny-service`, `com.journeyos.jrny`) é dono da **definição de jornadas e da decisão de
roteamento** dentro de um workspace (`empresa`): desenho de jornadas/estágios, regras de
roteamento versionadas, matrícula e avanço de leads, e o decision log imutável. A fronteira
**inclui**:

- O agregado `Jornada` e seus `Estagio` (definição versionada do funil).
- A `RegraRoteamento` e o motor de avaliação (Routing Engine).
- A `InscricaoJornada` (estado do lead na jornada) e a `DecisaoRoteamento` (decision log).
- A orquestração do assist de IA (chamada à TechLab AI `orchestration`).
- As projeções de telemetria/auditoria nos índices Elastic `journey-events` e `routing-decisions`.

A fronteira **exclui** (pertence a outros donos):

- Identidade, RBAC, contexto de tenant → **WRKS** (JRNY apenas consome `AccessDecision`/JWT).
- Captura, perfil, score e segmentação do lead → **LEAD** (JRNY **consome** os eventos).
- Conteúdo dos estágios (assets) → **ASST** (JRNY **referencia** assets publicados via Feign).
- **Execução** das ações: envio de mensagem → **COMM**; oportunidade/venda → **SALE**.
- Capacidade de IA (modelos, prompts, providers) → **TechLab AI** (consumida via HTTP).

## 2. External Actors and Systems

| Ator/Sistema | Tipo | Interação com JRNY |
|---|---|---|
| **HEAD_GROWTH / INFOPRODUTOR / SDR** | humano (via GWY → FE) | Desenho/publicação de jornadas e regras; leitura do estado de jornada dos leads. |
| **WRKS** | serviço (sync) | Valida JWT (JWKS) + `POST /access/evaluate` para autorização `jrny.*`. |
| **LEAD** | serviço (async) | Produz `lead.qualificado` / `lead.score.atualizado` / `lead.segmento.alterado` → gatilhos de roteamento. |
| **ASST** | serviço (sync + async) | Feign `AssetQueryClient` (conteúdo publicado dos estágios) + evento `asset.versao.publicada`. |
| **TechLab AI** | serviço externo (sync HTTP) | `orchestration` — recomendação de próximo-melhor-estágio (assist opcional, com fallback). |
| **Elasticsearch** | infra (sync, direct java client) | Índices `journey-events` + `routing-decisions` (fact) — telemetria/auditoria. |
| **PostgreSQL** (`emp_<slug>`) | infra | Fonte da verdade de jornadas, estágios, regras, inscrições e decisões. |
| **Kafka / AWS MSK** | infra (async) | Consome eventos LEAD/ASST/WRKS; produz eventos `journey-os.*` de roteamento. |
| **COMM / SALE** | serviço (sync + async) | Consomem estado/eventos de jornada (Feign `JourneyQueryClient` + `lead.roteado`/`estagio.transicionado`) para **executar** ações. |
| **MIG** | serviço | Prepara o schema do tenant (precondição). |

## 3. End-to-End Flows

### Golden path — *Lead qualificado → roteado → estágio avança → COMM/SALE agem*

```
LEAD
  → emite journey-os.lead.qualificado  (Kafka)
JRNY (consumer)
  → carrega a jornada PUBLICADA aplicável + inscricao_jornada do lead (cria se ausente)
  → Routing Engine avalia regra_roteamento (condições sobre score/segmento/atributo)
        → (opcional) consulta TechLab AI orchestration p/ recomendação de próximo estágio
        → se IA indisponível/timeout → decide só com as regras (fallback determinístico)
  → decide o estágio-alvo → avança a inscricao_jornada
  → grava DecisaoRoteamento (imutável): snapshot de entrada, regra disparada, assistIA, alvo, motivo
        → indexa em Elastic routing-decisions (fact)
  → emite journey-os.lead.roteado (âncora) + journey-os.estagio.transicionado
        → indexa transição em Elastic journey-events (fact)
COMM/SALE (consumers)
  → reagem ao evento (COMM envia mensagem do estágio; SALE cria oportunidade na OFERTA/FECHAMENTO)
  → leitura adicional do estado via Feign JourneyQueryClient se necessário
```

### Fluxos alternativos

- **Reavaliação por mudança de sinal:** `lead.score.atualizado` ou `lead.segmento.alterado` → reavalia regras; se uma dispara, reroteia (nova `DecisaoRoteamento`); se nenhuma, mantém o estágio (decisão `SEM_MUDANCA` registrada).
- **Sem jornada aplicável:** se nenhuma `jornada` PUBLICADA casa com o lead → decisão `NAO_ROTEADO` registrada (auditável); sem evento de avanço.
- **TechLab AI indisponível:** Routing Engine decide só com regras; a `DecisaoRoteamento` marca `assistIA=INDISPONIVEL`. Nenhum bloqueio (ver `ADR-003`/`ADR-005`).
- **Conclusão de jornada:** ao atingir um estágio terminal (`FECHAMENTO`/`POS_VENDA` configurado como final) → emite `journey-os.jornada.concluida`.
- **Conteúdo de estágio atualizado:** `asset.versao.publicada` → atualiza a referência de conteúdo vigente do estágio (sem reroteamento).
- **Publicação de jornada:** Marina/Rafael publica uma jornada (`RASCUNHO → PUBLICADA`) → emite `journey-os.jornada.publicada`; inscrições ativas seguem na versão em que entraram (`ADR-005`).

## 4. Internal Boundaries (camadas hexagonais)

```
api/            controllers REST (/api/v1/journeys/**, /api/v1/routing/**), DTO records, @RestControllerAdvice
application/    use cases (@Service, @Transactional): CriarJornada, PublicarJornada, DefinirRegra,
                RotearLead, AvancarEstagio, ConsultarJornadaDoLead; ports in/out
domain/         Jornada, Estagio, RegraRoteamento, InscricaoJornada, DecisaoRoteamento,
                EstadoJornada (state machine), MotorRoteamento (avaliação de regras) — POJO puro;
                domain services (avaliação determinística, transição) — zero Spring/JPA
infrastructure/ persistence (JPA emp_<slug>), clients (Feign WRKS + Feign ASST + client TechLab AI),
                messaging (producer/consumer Kafka), search (Elastic adapters journey-events/routing-decisions),
                security (EmpresaContextHolder, filtros JWT), config (DomainServiceConfig, Resilience4jConfig)
```

Regras ArchUnit RULE-01..09 (ver `ADR-001` e `hexagonal-patterns.md`).

## 5. Cross-cutting Concerns

- **Security / multi-tenancy:** todo request/evento carrega contexto de empresa; JWT validado contra JWKS de WRKS; `EmpresaContextHolder.require()` fixa o `emp_<slug>`; autorização por permissões `jrny.<recurso>.<acao>` via `AccessDecision` (cache curto, invalidado por `modelo.acesso.alterado`). Consumo de eventos resolve a empresa pelo payload/header e fixa o contexto antes de processar.
- **Observability:** MDC com `correlationId` + `empresaId` + `leadId`; logs estruturados (SLF4J/Lombok); métricas de latência da avaliação de regras e da chamada TechLab AI; taxa de fallback determinístico (assist indisponível).
- **Resiliência:** chamada à TechLab AI com timeout + circuit breaker (Resilience4j) + fallback determinístico; consumo de eventos idempotente (chave de evento); produção de eventos com outbox (ver SPEC-05).
- **Auditabilidade (decision log):** toda decisão de roteamento é persistida imutável e projetada em `routing-decisions` — requisito de produto, não apenas observabilidade.
- **LGPD:** decisões e snapshots podem conter atributos pessoais do lead → retenção/anonimização por tenant; decision log preserva trilha estrutural.
- **Idempotência:** processar o mesmo evento de domínio duas vezes não duplica matrícula/decisão (chave idempotente por evento+lead+versão de regra).

---

## Referências

- `01-architectural-vision.md` · `03-initial-domain-framing.md` · `04-backend-architecture-direction.md`
- `docs/architecture/backend/standards/hexagonal-patterns.md` · `platform-patterns.md`
- `docs/architecture/integrations/techlab-ai-integration.md` · `elastic-data-contract.md`
