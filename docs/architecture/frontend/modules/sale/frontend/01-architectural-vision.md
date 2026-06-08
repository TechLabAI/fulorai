# 01 — Architectural Vision — SALE (Sales & Revenue) · Frontend

> Camada de visão FE (Layer 1 — Architect). Gera contratos de UX/UI, não código Angular.
> Módulo: **SALE** · module `sale` · app `apps/sale` · libs `libs/sale/*` · scope `scope:sale`.
> Espelha o domínio do `sale-service` (BE) — aqui o recorte é a **experiência do usuário**.

## 1. Intent

Ao final, **Lucas (SDR/closer)** consegue abrir o Journey OS e ver, num **Kanban**, todas as
oportunidades da `empresa` organizadas por estágio — e **arrastar um card** de coluna para avançar o
deal, abrir uma oportunidade e **ganhar ou perder** com motivo. **Rafael (infoprodutor)** abre um
**dashboard de receita** e enxerga **quanto** faturou e **de qual origem** veio, além do **LTV** dos
melhores contatos. **Marina (Head de Growth)** consulta o **breakdown de atribuição** de cada compra
e governa os **modelos de atribuição** (cria uma versão, ativa, re-atribui) para provar o ROI por
origem/campanha. O FE SALE transforma fechamentos dispersos (DM, call, checkout) numa **superfície de
receita rastreável, explicável e acionável** — nunca um total opaco.

## 2. Problem Statement

**Jornada atual:** a operação fecha vendas em Hotmart, links de pagamento, DMs e planilhas de closer;
não há **pipeline único** e ninguém sabe dizer **de onde veio cada real**. Lucas perde o histórico de
ganho/perda; Rafael soma faturamento "no olho"; Marina não consegue provar o ROI de uma campanha
porque a receita não está ligada à origem do lead.

**Jornada nova (com o FE SALE):**

- **Pipeline único em Kanban** — uma board por estágio, com **drag-and-drop** para mover a oportunidade
  e filtros por responsável/estado; o closer vê o funil inteiro e age direto no card.
- **Fechamento rastreável** — abrir a oportunidade mostra lead vinculado, valor, responsável,
  probabilidade e **histórico de estágio**; ganhar/perder exige **motivo** (em perda) e fica auditável.
- **Receita explicável** — a compra confirmada (que chega server-to-server) é consultável com seu
  **breakdown de atribuição** (touchpoints + versão de modelo); o número nunca aparece sozinho.
- **Atribuição governável** — modelos versionados (last/first/linear-touch) listados, com ativação
  explícita que **re-atribui** as compras afetadas de forma rastreável.
- **Receita visível** — dashboard de funil por origem/período + LTV dos top contatos (read-only).

Sem o FE SALE, cada relatório de faturamento reinventaria "quanto vendemos e por quê", gerando números
divergentes e nenhuma ligação confiável entre marketing e receita.

## 3. Personas

| Persona | Papel canônico | Job-to-be-done no FE SALE |
|---|---|---|
| **Lucas — SDR / Closer** | `SDR` | **Principal.** Opera o **Kanban**: pega oportunidades, **arrasta** para mover estágio, registra **ganho/perda** com motivo. Vê apenas o seu `data_scope`. Não governa ofertas/modelos de atribuição. |
| **Rafael — Infoprodutor / CEO** | `INFOPRODUTOR` | **Secundária.** Acompanha **faturamento, LTV e saúde do funil** no dashboard de receita; consulta compras. Read-only de alto nível. |
| **Marina — Head de Growth** | `HEAD_GROWTH` | **Terciária.** Analisa **atribuição/ROI** por origem e campanha; governa **modelos de atribuição** (cria versão, ativa, re-atribui); cataloga **ofertas**. |
| **Serviços do Journey OS** (LEAD, JRNY, INTL, COMM) | — (máquina) | LEAD emite `lead.qualificado` → SALE cria/prioriza oportunidade; JRNY/INTL/COMM consomem eventos `oportunidade.*`/`compra.*`/`receita.*` via BE — **fora** da UI SALE. |

## 4. MVP Scope (in) — telas e fluxos

1. **Pipeline** (`feature-pipeline`) — **Kanban** de oportunidades por estágio (colunas = estágios,
   cards = oportunidades) com **drag para mover estágio** (`PATCH /oportunidades/{id}/estagio`),
   filtros por responsável/estado. Centerpiece do módulo (ver `ADR-005`).
2. **Detalhe da oportunidade** (`feature-opportunity`) — lead vinculado, valor estimado, responsável,
   probabilidade, **histórico de estágio**; ações **ganhar** / **perder** (motivo **obrigatório** na
   perda). Fechamento é terminal (espelha `409 sale.oportunidade.ja-fechada`).
3. **Ofertas** (`feature-offer`) — catálogo de `oferta` (produto + preço + moeda + vigência),
   **versionado**: criar; **editar** (gera **nova versão**, mantém as anteriores imutáveis);
   **desativar**.
4. **Compras** (`feature-purchase`) — lista/busca + detalhe (itens + **breakdown de atribuição**);
   ações **estornar** / **cancelar**. A ingestão é **server-to-server** (checkout/gateway) — o FE
   **não** dispara `POST /compras`; apenas **consulta** e ajusta (estorno/cancelamento recalculam
   receita/LTV no BE sem apagar histórico).
5. **Atribuição** (`feature-attribution`) — listar **versões** de `modelo_atribuicao`; criar versão
   (inativa); **ativar** (re-atribui as compras afetadas); ver o **breakdown** de uma compra
   (touchpoints + tipo + versão). Determinístico/explicável — mostra o modelo, nunca caixa-preta.
6. **Dashboard de receita** (`feature-revenue-dashboard`) — **funil de receita** por origem/período +
   **LTV** (top contatos por valor). Read-only, apoiado em Elastic (`revenue-events`/`campaign-events`).
7. **Guards** — todas as rotas são pós-contexto: `authGuard` + `empresaGuard` + `accessGuard('sale.*')`.

## 5. Out of Scope (MVP)

- **Scoring/qualificação** de lead — UI de **LEAD**.
- **Roteamento/atribuição** de SDR a lead — UI de **JRNY** (SALE consome a decisão via BE).
- **Comunicação/nutrição** — UI de **COMM**.
- **Processamento de pagamento** real (cobrar cartão, antifraude) — gateway/checkout é externo; SALE
  só registra a compra **já confirmada** (server-to-server). **Não há tela de registro de compra.**
- **Reconciliação contábil completa** (impostos, split, chargeback avançado) — MVP registra status básico.
- **Forecast de receita por ML** — previsão preditiva é pós-MVP.
- **Editor visual** (canvas drag-and-drop) de pipeline ou de modelo de atribuição — MVP via
  formulário/config (o drag-and-drop existe **só** para mover estágio no Kanban, não para editar o pipeline).
- **Atribuição probabilística/data-driven** treinada — MVP usa modelos determinísticos (last/first/linear-touch).

## 6. Architectural Principles

1. **Pipeline como Kanban com drag-and-drop (FE)** — mover estágio é a interação central; CDK DragDrop
   + signals com **optimistic move + rollback** em falha (ver `ADR-005`).
2. **Receita explicável, nunca caixa-preta (FE)** — toda exibição de atribuição mostra o **breakdown
   por touchpoint** + a **versão do modelo**; o total atribuído nunca aparece sozinho.
3. **Standalone-first** nas features; **Signals-first** no estado de UI (sem NgRx — `ADR-002`);
   **Lazy-by-default** (entry como library — `ADR-003`); **OnPush** obrigatório; NgModule só no entry lazy.
4. **module-pattern canônico** — slicing de libs por módulo idêntico aos demais (ver `ADR-001`).
5. **Sem IA no MVP** — o FE SALE **não** chama IA nem reflete badge de assist; atribuição e LTV são
   determinísticos. (Contraste com LEAD/ASST/COMM, onde a IA é assist BE-side refletido na UI.)
6. **SALE registra, não cobra (FE)** — o registro de compra é server-to-server; a UI **consulta** e
   **ajusta** (estornar/cancelar), nunca dispara o `POST /compras` de ingestão.
7. **Isolamento por empresa** — troca de empresa invalida pipeline/listas em tela antes de carregar os
   da nova empresa; nenhum dado cross-empresa (LGPD).
8. **Integração com o Shell via module registry** — descriptor + `ModuleShellIntegrationService`
   (ver `ADR-004`); SALE não conhece o Shell diretamente.

## 7. Success Signals

- Abrir o Kanban e mover uma oportunidade de estágio em **drag** com feedback imediato (optimistic) em
  < 1s p95; em falha (`409 ja-fechada`), o card volta para a coluna de origem com aviso — sem quebrar.
- Lucas marca **perder** sem motivo e a UI bloqueia com mensagem (espelha `422
  sale.oportunidade.motivo-obrigatorio`); com motivo, o deal fecha e some das colunas abertas.
- Rafael abre o dashboard e vê **quanto** faturou e **de qual origem** veio (atribuição), não só o total.
- Marina abre uma compra e lê o **breakdown** (touchpoints + versão de modelo); ativar uma nova versão
  de modelo reflete na UI (versão ativa destacada) e a re-atribuição é percebida de forma rastreável.
- Editar uma oferta cria uma **nova versão** na UI sem alterar as anteriores (versionamento visível).
- Trocar de empresa nunca mostra pipeline/compra da empresa anterior (cross-empresa guard de UI).
- Métricas Web Vitals dentro do orçamento: TTI < 3s, CLS < 0.1, FID/INP saudáveis mesmo com o Kanban
  carregado (virtual scroll por coluna se necessário); bundle lazy do SALE dentro do limite do módulo.
- 100% dos cenários do SPEC-08 viram spec Playwright descobrível (gate A5 e2e-validate).

---

## Referências

- ADRs: `adr/ADR-001..005`
- Brief: `../_brief.md`
- Blueprint: `02-architecture-blueprint.md`
- BE (espelho): `docs/architecture/backend/services/sale-service/{01,03}-*.md` + `contracts/api-contract.md`
- Multi-tenancy / Access Layer: `docs/architecture/frontend/standards/access-layer-contracts.md`
- module-pattern: `docs/architecture/frontend/standards/module-pattern.md`
