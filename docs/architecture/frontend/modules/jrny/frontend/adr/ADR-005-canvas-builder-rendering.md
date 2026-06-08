# ADR-005 — Renderização do Journey Builder: editor estruturado, não canvas livre — JRNY

- **Status:** accepted
- **Específico do JRNY** (decisão crítica extraída do brief)

## Contexto

O coração de autoria do JRNY é o **Journey Builder** — desenhar uma jornada como sequência de estágios
ordenados e tipados (`CAPTURA`…`POS_VENDA`). O brief BE é categórico em **dois** pontos:

1. O **canvas drag-and-drop visual** do Journey Builder é **responsabilidade do FE / pós-MVP** — o BE
   expõe API/modelo (`/api/v1/journeys`, estágios ordenados por `ordem`), não o desenho visual.
2. O modelo MVP é **estágios ordenados + regras de salto**, **não** um motor de workflow genérico com
   ramificação condicional arbitrária estilo BPMN.

O risco-chave de produto (R2) é o FE **over-investir num canvas de grafo livre** (lib de diagramação
pesada, layout automático, conexões arbitrárias) — inflando o bundle e o prazo para um recurto que o
próprio BE coloca fora do MVP. O risco espelhado (R3) é a UI permitir editar uma jornada **PUBLICADA**,
quebrando inscrições ativas.

## Decisão

O Journey Builder do MVP é um **editor estruturado de estágios ordenados**, não um canvas livre:

1. **Estágios como lista ordenada reordenável** — `feature-journey-builder` renderiza os estágios como
   uma **lista/stepper vertical** com reordenação (sortable: drag-handle ou setas ↑/↓ + teclado, a11y),
   refletindo o campo `ordem`. Sem grafo de nós/arestas, sem layout livre 2D.
2. **Sem lib de canvas/diagramação no MVP** — preferir componentes próprios (`libs/jrny/ui`:
   `stage-list`, `stage-card`) em SVG/CSS leves. Nenhuma dependência de diagramação (ex.: frameworks de
   flowchart) entra no bundle. A flag `jrny.journey-builder-canvas` nasce **off**, reservando o canvas
   visual para pós-MVP — quando ligada, carregaria a lib por **import dinâmico** (orçamento no SPEC).
3. **Regras como tabela, não arestas no canvas** — `feature-routing-engine` lista as `regra_roteamento`
   versionadas numa **smart-table** (origem→destino, condição resumida, prioridade, ativa, versão); a
   "ramificação" é expressa por regras priorizadas, não por conexões desenhadas.
4. **Imutabilidade do publicado, por construção** — toda a UI de edição (estágios, metadados, regras) é
   **desabilitada** quando `estadoJornada !== 'RASCUNHO'`; jornada `PUBLICADA` é read-only e o único CTA
   de mudança é **"criar nova versão"** (`POST /nova-versao`). Espelha `409 jrny.jornada.transicao-invalida`.
5. **Acessibilidade obrigatória** — reordenação operável por teclado; tipo/estado de estágio nunca
   dependem só de cor (sempre rótulo textual); contraste AA.

## Alternativas consideradas

- **Canvas drag-and-drop livre (lib de diagramação) no MVP** — rejeitada: o BE coloca o canvas como
  pós-MVP; custo de bundle/prazo desproporcional; o modelo MVP é estágios ordenados, não grafo livre.
- **Editor BPMN completo** — rejeitada: fora de escopo (sem ramificação condicional arbitrária no MVP).
- **Permitir edição inline de jornada PUBLICADA** — rejeitada: quebra a imutabilidade do publicado e as
  inscrições ativas (contradiz o princípio do BE).

## Consequências

**Positivas:** bundle enxuto (sem lib de canvas); entrega focada no que o BE suporta; a11y natural numa
lista/stepper; caminho claro de evolução (flag + import dinâmico) para o canvas pós-MVP; imutabilidade do
publicado garantida na UI. **Negativas:** a experiência de autoria é menos "visual" que um canvas (mitigado
por um stepper claro com preview do funil); reordenação acessível exige disciplina (drag + teclado);
quando o canvas pós-MVP chegar, parte da UI de builder será reescrita sobre a flag.

## Referências

- `_brief.md` (itens 4, 5 + notas) · `01-architectural-vision.md` (§5, §6) · `06-risks-gaps-assumptions.md` (R2, R3)
- BE: `jrny-service/_brief.md` (item 5 — canvas é FE/pós-MVP) · `01-architectural-vision.md` (§5, §6 P8) ·
  `contracts/api-contract.md` (`nova-versao`, `transicao-invalida`, estágios por `ordem`) ·
  `adr/ADR-005-routing-engine-model.md`
