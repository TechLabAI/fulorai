# 01 — Architectural Vision — INTL (Intelligence & Platform) · Frontend

> Camada de visão FE (Layer 1 — Architect). Gera contratos de UI, não código Angular.
> Módulo **INTL** · module `intl` · app lazy `apps/intl` · libs `libs/intl/*` · scope `scope:intl`.
> Espelha o domínio do `intl-service` (BE); aqui o recorte é a **experiência do usuário**.

## 1. Intent (UX-driven)

Ao final, o usuário do Journey OS consegue, a partir de uma superfície única:

1. **Perguntar em linguagem natural** ao **AI Copilot** sobre o próprio negócio e receber uma
   **resposta fundamentada** — com **citações clicáveis** que levam à evidência que sustenta a
   resposta. Quando o sistema não tem evidência suficiente (ou a IA está indisponível), a UI diz
   isso com clareza, **nunca** disfarçando uma resposta degradada de fato confirmado.
2. **Curar a Base de Conhecimento** (persona Marina): criar, editar, indexar e arquivar **nós de
   conhecimento** que alimentam o copiloto — vendo o estado de indexação de cada nó.
3. **Ler analítica consolidada** (persona Rafael): um **dashboard de funil** e um **painel de
   uso/custo do copiloto**, escopados à empresa ativa, sem montar relatório manual.

INTL é a **camada de inteligência do FE**: transforma dados dispersos em **respostas auditáveis**
e em **analítica confiável**. Seu produto de UX é **confiança** — toda síntese é rastreável até a
fonte, e todo dado é isolado por empresa.

## 2. Problem Statement (jornada atual vs nova)

**Jornada atual (Rafael / Marina):** os sinais do negócio estão espalhados — funil numa planilha,
ROI no gerenciador de ads, contexto de lead no CRM. Para responder "por que as vendas caíram esta
semana?" é preciso montar relatório à mão, cruzando ferramentas. Não há como **perguntar** ao
sistema, e quando se usa uma IA genérica ela **alucina** números sem fonte verificável.

**Jornada nova (Journey OS · INTL FE):** Rafael abre o Copilot, digita a pergunta e recebe em
segundos uma resposta **com chips de citação** — clica e vê o documento que a fundamenta. Marina
mantém a Base de Conhecimento curada para que o copiloto fique mais preciso. O dashboard de funil
consolida, num lugar só, o que antes vivia em cinco. Quando a IA não pode fundamentar, a UI mostra
um estado **degradado explícito** — a confiança vem de **nunca mentir sobre o que sabe**.

## 3. Personas (job-to-be-done)

| Persona | Papel canônico | Job-to-be-done no INTL FE |
|---|---|---|
| **Rafael — Infoprodutor / CEO** | `INFOPRODUTOR` | "Quero perguntar ao sistema o que está acontecendo no meu negócio e confiar na resposta — e ver meu funil e meu ROI consolidados, sem montar planilha." |
| **Marina — Head de Growth** | `HEAD_GROWTH` | "Quero manter a base de conhecimento da operação curada para o copiloto acertar mais, e analisar performance por origem/campanha." |
| **Lucas — SDR / Closer** | `SDR` | "Antes de uma call, quero pedir ao copiloto um resumo rápido do contexto do funil/lead — sem abrir cinco telas." |
| **Shell + módulos FE** | — (máquina) | Consomem a Access Layer (WRKS) que INTL também usa; podem deep-linkar para o Copilot com contexto (pós-MVP). |

## 4. MVP Scope (in) — telas, fluxos, formulários

1. **Copilot — lista de conversas + chat** — abrir nova conversa (`POST /copilot/conversas`),
   enviar pergunta (`POST .../perguntar`), renderizar a resposta com **citações** (chips →
   `documentoId`/`indice`/`trecho`) e **badge de status** (`RESPONDIDA` | `NAO_FUNDAMENTADA` |
   `DEGRADADA`). Estados de UI: `idle → pensando → respondida | degradada | erro`. Histórico via
   `GET /copilot/conversas/{id}`. Cancelamento de pergunta in-flight.
2. **Base de Conhecimento — lista/busca** — tabela de nós com filtros `?q=&tag=&status=` e
   paginação; ações por linha conforme permissão (editar, indexar, arquivar).
3. **Nó de conhecimento — criar/editar** — formulário (`titulo`, `conteudo`, `tags[]`, `fonte`);
   ação **Indexar** com estado assíncrono (`RASCUNHO → indexando → INDEXADO`), tratando `503`
   (`embedding-unavailable`) como "tente novamente" — não como erro fatal.
4. **Analytics — funil** — dashboard read-only do funil consolidado (`GET /analytics/funil`) com
   filtro de período/granularidade.
5. **Analytics — uso do copiloto** — painel de `totalRespostas`, `custoTokens`,
   `taxaFundamentadas`, `taxaDegradadas` (`GET /analytics/copilot`).
6. **Guards de acesso** — `authGuard`, `empresaGuard`, `accessGuard('intl.<perm>')` derivando
   visibilidade de rota/menu da Access Layer.
7. **Degradação graciosa na UI** — `DEGRADADA`/`NAO_FUNDAMENTADA` viram sinal visual explícito
   (badge + tooltip + sem citações fabricadas).

## 5. Out of Scope (MVP)

- **Streaming token-a-token (SSE)** da resposta — MVP é request/response com estado "pensando"
  (não há endpoint de streaming no BE; ver ADR-005). Streaming é pós-MVP.
- **Copilot com ações/automações** (escrita de volta em outros módulos, agentes que executam).
- **Editor rico de nós** (markdown avançado, anexos, upload) — MVP é texto + tags.
- **Dashboard builder / analytics preditivo / alerting** — pós-MVP (capability `analytics` do BE).
- **Viewer de observabilidade** (`app-logs`/`traces`/`metrics`/`integration-logs`) — sem UI de
  domínio no MVP.
- **Integration Hub** (conectores/webhooks 3rd-party) — pós-MVP.

## 6. Architectural Principles (FE)

1. **Standalone-first nas features** — toda feature e componente é `standalone`; `NgModule` não é
   usado no entry (entry é library `@journeyos/intl`, ADR-003 + ADR-006 global).
2. **Signals-first** — estado de UI em `signal<T>` privado nas facades + `.asReadonly()` público;
   **sem NgRx** (ADR-002).
3. **Lazy-by-default** — Shell carrega INTL via `loadChildren`/entry-lib; sub-rotas via
   `loadComponent`.
4. **OnPush mandatory** — todo componente usa `ChangeDetectionStrategy.OnPush`.
5. **A UI nunca decide acesso** — RBAC, sessão e empresa-context só via `@journeyos/shared/access-*`.
   Zero `if (role === ...)` em features; zero `localStorage` direto.
6. **Fundamentação acima de fluência** — a UI deriva o tratamento visual do `status` do BE; uma
   resposta sem citação fundamentada **nunca** é renderizada como fato confirmado (ADR-005).
7. **Isolamento de tenant na UI** — `empresaId` ativo só via `EmpresaContextService`; troca cancela
   in-flight + limpa conversa + recarrega Knowledge/Analytics (sem vazamento cross-empresa).
8. **Padrão module-pattern** — slicing canônico de libs por módulo (ADR-001).

## 7. Success Signals

- **TTI da tela do Copilot** < 2 s; o estado `pensando` aparece **imediatamente** após o envio da
  pergunta (feedback < 100 ms), mesmo com a resposta levando segundos.
- **100% das respostas `RESPONDIDA`** renderizam ≥ 1 citação clicável que resolve ao documento-fonte.
- **Respostas `DEGRADADA`/`NAO_FUNDAMENTADA`** são visualmente distintas e **nunca** exibem citação
  fabricada (0 falsos-positivos de fundamentação na UI).
- **Cancelamento** de uma pergunta in-flight encerra o estado `pensando` em < 200 ms.
- **Zero vazamento cross-empresa**: trocar de empresa limpa a conversa e recarrega Knowledge/Analytics;
  nenhuma resposta da empresa anterior aparece na nova.
- **Indexação de nó** reflete o estado real (`RASCUNHO`/`INDEXADO`) e trata `503` como retry, não
  como erro fatal.
- 100% dos cenários do SPEC-08 viram spec Playwright descobrível (gate e2e-validate / A5).

---

## Referências

- ADRs: `adr/ADR-001..005`
- Brief: `../_brief.md`
- Blueprint FE: `02-architecture-blueprint.md`
- BE espelho: `docs/architecture/backend/services/intl-service/01-architectural-vision.md`
- API BE: `docs/architecture/backend/services/intl-service/contracts/api-contract.md`
- Access Layer: `docs/architecture/frontend/standards/access-layer-contracts.md`
