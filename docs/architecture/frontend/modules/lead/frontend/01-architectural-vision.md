# 01 — Architectural Vision — LEAD (Lead Intelligence & Qualification) · Frontend

> Camada de visão FE (Layer 1 — Architect). Gera contratos de UX/UI, não código Angular.
> Módulo: **LEAD** · module `lead` · app `apps/lead` · libs `libs/lead/*` · scope `scope:lead`.
> Espelha o domínio do `lead-service` (BE) — aqui o recorte é a **experiência do usuário**.

## 1. Intent

Ao final, **Marina (Head de Growth)** consegue abrir o Journey OS e ver, numa **fila priorizada**,
quais leads da `empresa` estão prontos para comprar — e **por quê**. **Lucas (SDR)** abre um lead e
vê o **Maturity Score (6D)** desdobrado em 6 dimensões, com o quanto cada uma contribuiu e qual
versão de regra produziu aquele número. Marina desenha **segmentos** dinâmicos, configura **surveys**
que enriquecem o perfil e versiona **regras de qualificação** sem sair da UI. O FE LEAD transforma o
índice multidimensional do BE numa **superfície explicável e acionável** — nunca um número opaco.

## 2. Problem Statement

**Jornada atual:** o lead da mesma pessoa aparece repetido em planilhas diferentes; não há critério
único de prioridade. Marina não consegue afirmar com confiança "estes 200 estão prontos, estes 5.000
não"; Lucas recebe uma fila sem ordem e gasta tempo com quem não vai comprar. Quando existe algum
"score", é uma caixa-preta — ninguém sabe explicar de onde veio.

**Jornada nova (com o FE LEAD):**

- **Fila única e priorizada** — uma lista por Maturity Score, com filtros por segmento/dimensão/estado.
- **Score explicável** — abrir um lead mostra o **breakdown das 6 dimensões**, a versão de regra e se
  houve assist de IA; o número nunca aparece sozinho.
- **Segmentação visível** — predicados sobre perfil+score que reagrupam a base; o usuário vê quantos
  leads cada segmento contém e navega para a fila do segmento.
- **Qualificação governável** — versões de regra listadas, com ativação explícita e recálculo rastreável.
- **Perfil enriquecível** — surveys configuráveis cujas respostas atualizam o perfil e disparam recálculo.

Sem o FE LEAD, cada operador continuaria priorizando "no olho" e cada módulo a jusante (JRNY/SALE)
reinventaria a leitura de "quem é esse lead e quanto vale".

## 3. Personas

| Persona | Papel canônico | Job-to-be-done no FE LEAD |
|---|---|---|
| **Marina — Head de Growth** | `HEAD_GROWTH` | **Principal.** Monitora a **distribuição** do Maturity Score e a saúde da base; desenha **segmentos** e **regras de qualificação**; configura **surveys**. Quer enxergar a base inteira e ajustar os critérios. |
| **Lucas — SDR / Closer** | `SDR` | **Secundária.** Trabalha a **fila priorizada**; abre o lead e usa o **breakdown 6D** para decidir a abordagem. Vê apenas o seu `data_scope`. Não edita regras/segmentos. |
| **Rafael — Infoprodutor / CEO** | `INFOPRODUTOR` | **Terciária.** Visão consolidada de qualidade/volume qualificado da base (read-only de alto nível). |
| **Serviços do Journey OS** (JRNY, SALE, INTL) | — (máquina) | Consomem eventos `lead.*` via BE — **fora** da UI LEAD. |

## 4. MVP Scope (in) — telas e fluxos

1. **Fila de leads** (`feature-lead-list`) — lista priorizada por Maturity Score; filtros por
   segmento/dimensão/estado + busca; paginação; abre o detalhe. Backed por Elastic (`GET /leads`).
2. **Detalhe do lead** (`feature-lead-detail`) — perfil tipado (atributos + origem + base legal);
   **breakdown 6D** do score; ações: editar perfil, **forçar qualify** (recompute), **anonimizar**,
   **expurgar** (LGPD). Estado `ANONIMIZADO` trava edição.
3. **Maturity Score** (`feature-maturity-score`) — **radar 6D** reusável + **dashboard de distribuição**
   (histograma do score agregado, saúde por dimensão, % com assist IA). Leitura/monitoramento.
4. **Segmentação** (`feature-segmentation`) — CRUD de `segmento` (nome + predicado sobre perfil+score);
   prévia de contagem; navegação para a fila do segmento (`/segments/{id}/leads`).
5. **Surveys** (`feature-survey`) — definição de `survey` + `pergunta`; captura de respostas para um
   lead (atualiza perfil → dispara recálculo no BE).
6. **Qualification rules** (`feature-qualification-rules`) — listar versões; criar nova versão (inativa);
   **ativar** versão (desativa a anterior atomicamente no BE); forçar recálculo de afetados.
7. **Guards** — todas as rotas são pós-contexto: `authGuard` + `empresaGuard` + `accessGuard('lead.*')`.

## 5. Out of Scope (MVP)

- **Roteamento/atribuição** de lead a SDR/jornada — UI de **JRNY**.
- **Pipeline/oportunidade/venda** — UI de **SALE**.
- **Disparo de comunicação/nutrição** — UI de **COMM**.
- **Editor visual** (canvas drag-and-drop) de regras/predicados — MVP usa formulário estruturado +
  expressão textual validada.
- **Importação em massa / upload de CSV** com pipeline assíncrono — captura é mediada pelo BE/integrações.
- **UI de comparação/merge manual** de duplicados — MVP confia no dedup determinístico do BE
  (expõe apenas `duplicado=true`).
- **Analytics preditivo / scoring treinado por tenant** — fora do MVP.

## 6. Architectural Principles

1. **Score explicável, nunca caixa-preta (FE)** — toda exibição do Maturity Score mostra breakdown
   por dimensão + versão de regra + badge de assist IA (ver `ADR-005`).
2. **Standalone-first** nas features; **Signals-first** no estado de UI (sem NgRx — `ADR-002`);
   **Lazy-by-default** (entry como library — `ADR-003`); **OnPush** obrigatório; NgModule só no entry lazy.
3. **module-pattern canônico** — slicing de libs por módulo idêntico aos demais (ver `ADR-001`).
4. **IA é assist BE-side, refletido — não chamado** — o FE nunca conhece a TechLab AI; só reflete
   `assist_ia` e degrada visualmente (badge "score determinístico").
5. **Isolamento por empresa** — troca de empresa invalida fila/segmentos em tela antes de carregar os
   da nova empresa; nenhum dado cross-empresa (LGPD).
6. **Privacidade por design (LGPD)** — base legal/consentimento visíveis; ações anonimizar/expurgar
   gated; lead anonimizado trava edição na UI.
7. **Integração com o Shell via module registry** — descriptor + `ModuleShellIntegrationService`
   (ver `ADR-004`); LEAD não conhece o Shell diretamente.

## 7. Success Signals

- Abrir a fila e ordená-la por Maturity Score em < 1s p95 (lista paginada, Elastic-backed).
- Um SDR abre um lead e vê **por que** o score é alto — o radar 6D e a contribuição por dimensão,
  não só o número.
- Indisponibilidade da IA não quebra a UI: o lead aparece com badge "score determinístico" e segue
  acionável.
- Trocar de empresa nunca mostra lead/segmento da empresa anterior (cross-empresa guard de UI).
- Ativar uma nova versão de regra reflete na UI (versão ativa destacada) e o recálculo é percebido
  de forma rastreável.
- Lead `ANONIMIZADO` aparece com PII suprimida e edição desabilitada (espelha `409 lead.lead.anonimizado`).
- Métricas Web Vitals dentro do orçamento: TTI < 3s, CLS < 0.1, FID/INP saudáveis; bundle lazy do LEAD
  dentro do limite do módulo.
- 100% dos cenários do SPEC-08 viram spec Playwright descobrível (gate A5 e2e-validate).

---

## Referências

- ADRs: `adr/ADR-001..005`
- Brief: `../_brief.md`
- Blueprint: `02-architecture-blueprint.md`
- BE (espelho): `docs/architecture/backend/services/lead-service/{01,03}-*.md` + `contracts/api-contract.md`
- Multi-tenancy / Access Layer: `docs/architecture/frontend/standards/access-layer-contracts.md`
- module-pattern: `docs/architecture/frontend/standards/module-pattern.md`
