# 01 — Architectural Vision — ASST (Asset Hub) · Frontend

> Camada de visão (Layer 1 — Architect). Gera contratos, não código.
> Módulo: **ASST** · module `asst` · app lazy `apps/asst` · consome `asst-service` via GWY.
> Espelha a vision BE (`asst-service/01-architectural-vision.md`); recorte aqui é a **experiência do usuário**.

## 1. Intent

Ao final, **Marina** (Head de Growth) tem uma tela única onde catalogar, buscar e organizar todos
os ativos de conteúdo da operação; compor um rascunho de e-mail/landing/roteiro em segundos com o
**Asset Studio** (IA via TechLab AI, delegada pelo BE) em vez de partir da folha em branco; navegar
pelo histórico de versões imutáveis; e submeter o asset para aprovação. **Rafael** (Infoprodutor/CEO)
tem uma **fila de aprovações** onde aprova, rejeita (com comentário) e **publica** — tornando a versão
vigente disponível para o resto do Journey OS. A UI torna explícito o que hoje é informal: qual é a
versão vigente, quem aprovou, e de onde veio cada conteúdo (proveniência manual vs Asset Studio).

## 2. Problem Statement

**Jornada atual:** os ativos vivem espalhados em Drive + Notion + Canva + WhatsApp. "Qual é o e-mail
aprovado?" vira arqueologia de pastas; a aprovação do Rafael acontece informalmente e some; um roteiro
que converteu é copiado-e-colado, perdendo proveniência; escrever a primeira versão do zero é gargalo.

**Jornada nova (FE ASST):**

- **Catálogo único** — toda a produção em um lugar, filtrável por tipo/tag/estado e buscável por
  full-text; a versão vigente publicada é sempre identificável.
- **Trilha de aprovação visível** — submeter/aprovar/rejeitar/publicar são ações de UI gated por
  permissão; a decisão (revisor, comentário, timestamp) fica registrada e recuperável.
- **Composição assistida** — o Asset Studio compõe um rascunho a partir de um brief + contexto da
  empresa, marcado com `origem=ASSET_STUDIO`, que o usuário revisa antes de submeter.
- **Reuso com proveniência** — versões imutáveis preservam a história; consumidores (COMM/JRNY/SALE)
  recebem deterministicamente a versão publicada.

## 3. Personas

| Persona | Papel canônico | Relação com ASST (FE) |
|---|---|---|
| **Marina — Head de Growth** | `HEAD_GROWTH` | Persona **principal**. Cria assets, usa o Asset Studio para compor rascunhos, organiza por tipo/tag, edita conteúdo de versão e submete para aprovação. |
| **Rafael — Infoprodutor / CEO** | `INFOPRODUTOR` | Persona **secundária**, **autoridade de publicação**: usa a fila de aprovações para aprovar/rejeitar e **publicar**. |
| **Lucas — SDR / Closer** | `SDR` | Consumidor de leitura: visualiza assets/scripts **publicados**; `data_scope` restringe o que enxerga; sem ações de autoria/aprovação (a UI as esconde via RBAC). |
| **Serviços do Journey OS** (COMM, JRNY, SALE) | — (máquina) | Consomem assets **publicados** via API BE/eventos — **não** pela UI ASST. |

## 4. MVP Scope (in)

1. **Catálogo + busca** — `feature-asset-library`: grade/tabela de assets com filtros (`tipoAsset`,
   tag, estado) + busca full-text + paginação; estado vazio/loading/erro.
2. **Criação + metadados** — criar asset (`RASCUNHO`), editar título/descrição/tags; arquivar.
3. **Detalhe + versões** — `feature-asset-detail`: dados do asset, estado atual, **histórico de
   versões imutáveis** (timeline), conteúdo de uma versão, versão vigente publicada; criar nova
   versão manual (conteúdo estruturado/texto + binário **por URL**).
4. **Asset Studio** — `feature-asset-studio`: formulário de brief + contexto → `POST /studio/compose`
   → nova versão `RASCUNHO` (`origem=ASSET_STUDIO`); loading explícito, timeout e **degradação
   graciosa** quando a IA está indisponível.
5. **Approval workflow** — `feature-approval-workflow`: submeter, fila de aprovações, aprovar/rejeitar
   (com comentário), publicar; refletindo a state machine `RASCUNHO → EM_REVISAO → APROVADO → PUBLICADO`
   (+ `REJEITADO`).
6. **Guards de acesso** — `authGuard`, `empresaGuard`, `accessGuard('asst.<perm>')` consumindo
   `AccessDecisionService`; ações de autoria/aprovação aparecem só para quem tem a permissão.

## 5. Out of Scope (MVP)

- **Upload/hospedagem de binários pesados** (vídeo/imagem) — binários são **referenciados por URL
  externa**; sem chunked-upload, sem transcoding, sem CDN no FE ASST.
- Edição colaborativa em tempo real (co-editing / CRDT).
- Editor rich-text/WYSIWYG avançado — MVP edita conteúdo estruturado/texto simples.
- A/B testing de variantes; brand kit / design system; tradução multilíngue.
- Aprovação multi-nível com SLA/escalonamento — MVP é aprovação **single-step**.

> **Nota de escopo:** o master plan FE (versão pré-brief) sugeria `feature-asset-upload` + ADR-005
> `chunked-upload-strategy`. O brief BE **autoritativo** coloca upload de binário fora do MVP
> (referência por URL). Esta vision segue o brief; ADR-005 trata da **composição assistida / degradação
> da IA** (a decisão crítica real do ASST), e o master plan será corrigido na atualização do autopilot.

## 6. Architectural Principles

1. **Standalone-first** nas features (`feature-asset-library`, `-detail`, `-studio`,
   `-approval-workflow`); `OnPush` mandatório em todo componente.
2. **Signals-first** — estado de tela em `signal<T>` privado + `.asReadonly()` na facade; sem NgRx,
   sem `BehaviorSubject` manual (ver ADR-002).
3. **Lazy-by-default** — `asst.module.ts` é o único `NgModule`, carregado pelo Shell via
   `loadChildren`; sub-rotas via `loadComponent` (ver ADR-003).
4. **IA é capacidade delegada e degradável** — o Asset Studio chama só o BE; falha da IA degrada
   **apenas** o Studio, nunca catálogo/versão/aprovação (ver ADR-005).
5. **Versão imutável é a verdade** — a UI nunca edita uma versão existente; corrigir = nova versão.
6. **Isolamento por empresa** — todo dado escopado por `empresaId`; troca de empresa invalida o
   catálogo em tela antes de renderizar o da nova empresa (sem vazamento cross-empresa).
7. **RBAC não é decidido na UI** — visibilidade de ação só via `AccessDecisionService.can('asst.*')`.

## 7. Success Signals

- Marina compõe um rascunho de e-mail no Asset Studio em < 1 min (brief → versão `RASCUNHO` visível),
  com indicação clara de proveniência (`origem=ASSET_STUDIO`).
- Rafael abre a fila de aprovações, aprova/rejeita com comentário, e publica — a decisão fica
  registrada e a versão vigente muda deterministicamente na tela.
- Buscar "template de boas-vindas" retorna a versão **publicada** vigente, com proveniência.
- TechLab AI indisponível: o Asset Studio mostra degradação explícita; catálogo, versionamento e
  aprovação continuam 100% funcionais (testado em e2e dedicado).
- Nenhuma requisição da empresa A renderiza asset da empresa B (cross-empresa guard; e2e).
- Métricas de UX: TTI do catálogo < 2,5 s; p95 da chamada de lista < 800 ms; taxa de conclusão do
  golden path (criar→compor→submeter→aprovar→publicar) medida via `@journeyos/shared/observability`.

---

## Referências

- ADRs: `adr/ADR-001..005`
- Brief: `_brief.md`
- Blueprint: `02-architecture-blueprint.md`
- BE espelho: `docs/architecture/backend/services/asst-service/01-architectural-vision.md`
- TechLab AI: `docs/architecture/integrations/techlab-ai-integration.md`
- Access Layer: `docs/architecture/frontend/standards/access-layer-contracts.md`
