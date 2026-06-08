# 06 — Risks, Gaps & Assumptions — JRNY (Journey & Routing)

> Itens a validar antes/durante specs e implementação. Cada risco com mitigação.

## 1. Riscos

| # | Risco | Impacto | Mitigação |
|---|---|---|---|
| R1 | **TechLab AI indisponível/lento** degrada o assist de roteamento | Baixo | Assist é **opcional**: timeout + circuit breaker + fallback determinístico; regras decidem sozinhas (`ADR-003`/`ADR-005`). |
| R2 | **Regras conflitantes/ambíguas** roteiam lead para alvo errado | Alto | `prioridade` explícita + avaliação determinística ordenada; decision log audita a regra disparada; testes BDD por cenário de regra. |
| R3 | **Reprocessamento de eventos** (LEAD) duplica matrícula/decisão | Médio | Consumo idempotente (chave evento+lead+versão de regra); unique parcial em `inscricao_jornada` ATIVA. |
| R4 | **Inconsistência PostgreSQL ↔ Elastic** (`journey-events`/`routing-decisions`) | Médio | Elastic é projeção; index best-effort; reconciliação periódica; PostgreSQL é fonte da verdade. |
| R5 | **Mudança de jornada sob inscrições ativas** corrompe execução | Alto | Versionamento: inscrição referencia a `jornada_versao` de entrada; `PUBLICADA` não é editada in-place (`ADR-005`). |
| R6 | **Vazamento cross-empresa** | Alto | `EmpresaContextHolder.require()` + `empresa_id` guard + testes de isolamento; schema-per-tenant. |
| R7 | **Acoplamento com COMM/SALE** (JRNY executando ações) | Médio | JRNY **decide e sinaliza** via evento; execução é de COMM/SALE; contrato de leitura via Feign `JourneyQueryClient`. |
| R8 | **Referência a lead/asset de outro módulo** desatualizada | Baixo | `lead_id`/`asset_ref_id` são referências lógicas; reage a `asset.versao.publicada`; LEAD é fonte do estado do lead. |

## 2. Gaps Conhecidos

- **Contrato TechLab AI `orchestration` não pinado:** `integrations/techlab-ai/openapi.json` e `techlab-ai-integration.md` ainda são placeholders (P3 bloqueado — aguarda 1º commit upstream). O endpoint/DTO exato do assist de roteamento será fixado quando o SHA for pinado.
- **Modelo de `condicao` (regra de roteamento):** a gramática do predicado jsonb (operadores, campos do lead disponíveis: score 6D, segmento, atributos) será detalhada nas specs (`data-model.md` + SPECs). Depende do contrato de eventos de LEAD (payload de `lead.qualificado`/`score.atualizado`).
- **Permissões `jrny.*`:** o conjunto canônico (`jrny.jornada.criar/editar/publicar/arquivar/ler`, `jrny.regra.criar/editar`, `jrny.roteamento.ler`) precisa ser confirmado no RBAC global (`shared/rbac/permissoes.md`).
- **Estágios terminais e conclusão:** a definição de qual estágio encerra a jornada (e o que conta como "concluída" vs "encerrada") será refinada nas specs.
- **Contrato de leitura para COMM/SALE:** a superfície do `JourneyQueryClient` (o que COMM/SALE precisam ler do estado de jornada) será detalhada quando esses módulos forem arquitetados.

## 3. Suposições a Validar

1. JRNY **decide e sinaliza**, não executa ações de canal/venda — COMM/SALE consomem os eventos e agem. (A validar com produto.)
2. O assist de IA (`orchestration`) é **sempre opcional**; o roteamento determinístico é o caminho de referência e nunca depende da IA.
3. Os 6 tipos de estágio do MVP (`CAPTURA`..`POS_VENDA`) cobrem o funil inicial; novos tipos são extensão de catálogo.
4. O modelo MVP é "estágios ordenados + regras de salto", não um motor BPMN genérico.
5. O lead referenciado (`lead_id`) e seus atributos vêm de LEAD via eventos; JRNY não duplica o perfil do lead, apenas o snapshot necessário à decisão.
6. Os índices Elastic `journey-events`/`routing-decisions` são **fact** (append-only), reconstruíveis do PostgreSQL.

## 4. Dependências Críticas

| Dependência | Estado | Bloqueia |
|---|---|---|
| **WRKS** (identidade/RBAC/AccessDecision) | vision+specs+scaffold OK | Autorização `jrny.*` em runtime (não bloqueia a arquitetura/scaffold de JRNY). |
| **LEAD** (eventos de qualificação/score/segmento) | vision+specs OK; backlog/scaffold pendentes | Gatilho de roteamento em runtime; o **contrato de payload** dos eventos informa o modelo de `condicao` (gap acima). Não bloqueia vision/specs de JRNY. |
| **ASST** (`AssetQueryClient`, `asset.versao.publicada`) | vision+specs+backlog OK; scaffold em andamento | Conteúdo de estágio em runtime (não bloqueia arquitetura de JRNY). |
| **MIG** (schema `emp_<slug>`) | scaffold OK | Execução local (`bootRun`) — não bloqueia specs/scaffold. |
| **TechLab AI** (`orchestration`) | P3 bloqueado (placeholder) | Detalhamento fino do contrato do assist nas specs; geração de DTOs no scaffold. Assist é opcional → não bloqueia o golden path. |
| **Elastic** índices `journey-events`/`routing-decisions` | declarados em `project-context.json` | Telemetria/auditoria; contrato em `elastic-data-contract.md`. |
| **REG/GWY** | scaffold OK | Discovery/edge em runtime. |

> **Nota para o autopilot:** as dependências de WRKS/LEAD/ASST são de **runtime** (e de
> refinamento de contrato), não de arquitetura. A pipeline vision→specs→backlog→scaffold de JRNY
> pode prosseguir. O contrato fino da TechLab AI (`orchestration`) permanece como gap até o SHA
> upstream ser pinado — as specs devem modelar o assist contra a interface esperada, marcar o
> ponto exato de acoplamento e garantir o caminho determinístico como padrão. O modelo de
> `condicao` deve referenciar o payload de eventos de LEAD (já especificado em `lead-service`).

---

## Referências

- `01-architectural-vision.md` (§5 Out of Scope) · `04-backend-architecture-direction.md`
- `adr/ADR-003-messaging-strategy.md` · `adr/ADR-005-routing-engine-model.md`
- `docs/architecture/integrations/techlab-ai-integration.md` (placeholder — P3)
