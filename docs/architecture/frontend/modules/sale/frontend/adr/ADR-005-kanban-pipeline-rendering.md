# ADR-005 — Renderização do pipeline como Kanban (drag-and-drop + optimistic move) — SALE

- **Status:** accepted
- **Específico do SALE** (decisão crítica extraída do brief)

## Contexto

O coração operacional do SALE é o **pipeline de vendas**: oportunidades (deals) que se movem por
**estágios** (`NOVA → CONTATO → PROPOSTA → GANHA/PERDIDA`) até o fechamento. A persona principal é o
**SDR/closer (Lucas)**, que precisa de uma leitura de funil **imediata** e de uma forma **rápida e
natural** de avançar um deal. O brief BE define o estágio como atributo configurável da oportunidade,
com transição via `PATCH /oportunidades/{id}/estagio` (que registra `historico_estagio` e publica
`oportunidade.estagio.alterado`); e define que fechamento é **terminal** (`409
sale.oportunidade.ja-fechada` ao tentar fechar/mover um deal já `GANHA`/`PERDIDA`). A decisão de UI
crítica é **como renderizar e operar esse pipeline** sem latência percebida e sem inconsistência de estado.

## Decisão

O pipeline do SALE é renderizado como um **board Kanban** com **drag-and-drop para mover estágio**:

1. **Layout Kanban.** Colunas = **estágios** (na ordem do pipeline); cards = **oportunidades**. Cada
   coluna mostra contagem e soma de valor estimado; cada card mostra título (lead+oferta), valor,
   responsável e probabilidade. Componentes em `libs/sale/ui` (`kanban-board`, `kanban-column`,
   `opportunity-card`).
2. **Drag-and-drop via Angular CDK DragDrop** (`@angular/cdk/drag-drop`), **não** HTML5 DnD nativo:
   acessibilidade, suporte a teclado, listas conectadas (`cdkDropListGroup`) e previsibilidade de
   eventos são melhores. Soltar o card numa coluna dispara `PATCH /oportunidades/{id}/estagio`.
3. **Optimistic move + rollback** (estado em signals — ADR-002): ao soltar, a UI **move o card
   imediatamente** e marca `movingCardId`; em **sucesso**, confirma a posição e o histórico; em
   **falha** (`409 sale.oportunidade.ja-fechada`, rede, `403`), faz **rollback** — o card volta para a
   coluna de origem (último estado confirmado) + toast de erro. Nunca persiste estado inconsistente.
4. **Fechamento é terminal.** Oportunidades `GANHA`/`PERDIDA` não são arrastáveis para reabrir; o
   `ganhar`/`perder` é ação no detalhe (`feature-opportunity`), com **motivo obrigatório** na perda
   (`422 sale.oportunidade.motivo-obrigatorio`).
5. **Performance.** Para pipelines grandes, virtual scroll por coluna (CDK) e/ou paginação/lazy de
   cards; `GET /oportunidades` paginado/filtrado server-side por responsável/estado. O CDK DragDrop
   é importado **só** no `feature-pipeline` (orçamento de bundle no SPEC).

## Alternativas consideradas

- **Tabela/lista simples** (mover estágio por dropdown na linha) — rejeitada como experiência primária:
  não dá a leitura de funil que o closer precisa; reservada como **fallback de acessibilidade**
  (mover estágio via menu/teclado) e para viewports estreitos.
- **HTML5 Drag-and-Drop nativo** — rejeitada: pior acessibilidade/teclado, eventos inconsistentes entre
  browsers, sem listas conectadas prontas. CDK DragDrop resolve isso de forma padronizada.
- **Sem optimistic update** (mostrar spinner e só mover após o `PATCH`) — rejeitada: latência percebida
  alta numa interação de alta frequência; o optimistic+rollback dá fluidez sem abrir mão da correção.
- **Virtualização agressiva sempre** — adiada: complexidade desproporcional ao volume típico do MVP;
  introduzir só se R2 (Kanban grande) se confirmar.

## Consequências

**Positivas:** leitura de funil imediata e operação fluida para o SDR; correção garantida pelo rollback
(o BE é a autoridade do estágio); acessível (CDK + fallback de lista); reaproveitável como pattern
shared se JRNY/outros precisarem de board. **Negativas:** mais componentes de UI a construir/testar
(`kanban-board`, `kanban-column`, `opportunity-card`) e disciplina de rollback/snapshot; CDK DragDrop
soma ao bundle do `feature-pipeline`; a11y do drag exige cuidado (fallback de teclado/lista).

## Referências

- `_brief.md` (itens 4, 8 + notas) · `01-architectural-vision.md` (§6, §7) · `03-domain-framing-frontend.md` (§3, §4)
- `05-state-and-data-flow.md` (§4 optimistic move + rollback)
- BE: `sale-service/contracts/api-contract.md` (`PATCH /oportunidades/{id}/estagio`,
  `409 sale.oportunidade.ja-fechada`, `422 sale.oportunidade.motivo-obrigatorio`) ·
  `sale-service/03-initial-domain-framing.md` (estados/transições) · `adr/ADR-005` (atribuição/idempotência)
- ADR-002 (signals-first — base do optimistic+rollback)
