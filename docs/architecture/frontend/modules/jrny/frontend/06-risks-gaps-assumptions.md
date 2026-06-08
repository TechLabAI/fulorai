# 06 — Risks, Gaps and Assumptions — JRNY (Journey & Routing)

> Riscos, gaps conhecidos, suposições a validar e dependências críticas do FE JRNY.

## 1. Riscos

| # | Risco | Impacto | Mitigação |
|---|---|---|---|
| **R1** | **Decisão de roteamento como caixa-preta** — a UI mostrar só o estágio-alvo sem o "por quê", ou tratar `assistIa=false` como erro. | Perda de confiança; contradiz o contrato BE (IA-off não é erro). | `ADR-005`: decision log explicável (gatilho+regra+alvo+assistIa+motivo); badge neutro para IA-off; a11y. |
| **R2** | **Over-engineering do builder** — investir num canvas drag-and-drop livre (lib pesada) no MVP. | Bundle inflado; prazo; escopo BE diz canvas é pós-MVP. | `ADR-005`: editor **estruturado** de estágios ordenados (sortable-list/stepper), sem lib de canvas; flag `journey-builder-canvas` off (reservada). |
| **R3** | **UI muta jornada PUBLICADA** — editar uma jornada vigente quebra inscrições ativas. | Inconsistência de estado; lead muda de definição embaixo. | Gate `RASCUNHO` em toda edição; PUBLICADA read-only; CTA "nova versão" (espelha `409 transicao-invalida`). |
| **R4** | **Contrato BE de `condicao`** (gramática de snapshot) instável/sub-especificado. | Editor de regra inconsistente com o BE. | Espelhar `data-model.md §5`; validação client-side mínima + confiar no `422 condicao-invalida`; sem query-builder visual no MVP. |
| **R5** | **Vazamento cross-empresa** ao trocar de empresa com builder aberto. | LGPD / dados de outra empresa em tela. | `effect()` na troca de empresa invalida jornadas/builder antes de carregar. |
| **R6** | **Acoplamento implícito a COMM/SALE/ASST/LEAD** na UI. | Quebra o princípio "decide e sinaliza"; fan-out cross-módulo. | Referências por id resolvidas pelo BE; sem chamada FE cross-módulo; JRNY não executa ações de canal/venda. |
| **R7** | **Performance** do builder com muitos estágios / decision log longo. | Jank no sortable; lista de decisões grande. | OnPush + signals; paginação do decision log; virtualização se SPEC exigir. |

## 2. Gaps Conhecidos

- **Gramática de `condicao`** das regras — depende de `jrny-service/contracts/data-model.md §5`; a UI do
  editor de regra precisa do detalhe exato dos campos/operadores permitidos (resolver na Specs).
- **Resolução de `assetRefId` → label** — o estágio referencia um asset publicado de ASST; como o FE
  obtém o **nome** do asset (cross-link BE vs id cru) precisa ser definido na Specs.
- **`journey-events` para analytics** — se o funil vem de endpoint REST do `jrny-service` ou de
  projeção Elastic exposta; o api-contract atual cobre journeys/routing, não analytics de funil
  (confirmar na Specs / com o BE).
- **Facade dedicada** (`libs/jrny/facade`) — decisão adiada para a Specs (ver `04` §3).

## 3. Suposições a Validar

- Volume de jornadas por empresa é **baixo-moderado** (dezenas) → lista paginada simples basta.
- Estágios por jornada na casa de **unidades a ~dezena** → sortable-list sem virtualização no MVP.
- Decision log por lead pode ser **longo** → paginação obrigatória (newest-first, como o BE).
- Devices-alvo: **desktop** (operação de growth); o builder não precisa ser mobile-first no MVP.
- Frequência de uso: builder/regras (Marina/Rafael, edição esporádica); decision log (Lucas, leitura
  frequente) → otimizar leitura do decision log.

## 4. Dependências Críticas

- **BE `jrny-service`**: `/api/v1/journeys/**` + `/api/v1/routing/**` (api-contract) — fonte única.
- **`condicao` grammar**: `jrny-service/contracts/data-model.md §5`.
- **Access Layer**: `@journeyos/shared/access-*` (auth/empresa/decision/http-base).
- **Design tokens**: `@journeyos/shared/ui-tokens`.
- **Gerador Nx**: `@journeyos/internal:module` (scaffold A4).
- **Cross-link de leitura**: resolução de `assetRefId` (ASST) e `leadId` (LEAD) — por id, BE-mediado.

---

## Referências

- `01-architectural-vision.md` (§7 success signals) · `adr/ADR-005-canvas-builder-rendering.md`
- BE: `jrny-service/06-risks-gaps-assumptions.md` · `contracts/{api-contract,data-model}.md`
