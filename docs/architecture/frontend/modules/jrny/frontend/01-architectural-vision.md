# 01 — Architectural Vision — JRNY (Journey & Routing) · Frontend

> Camada de visão FE (Layer 1 — Architect). Gera contratos de UX/UI, não código Angular.
> Módulo: **JRNY** · module `jrny` · app `apps/jrny` · libs `libs/jrny/*` · scope `scope:jrny`.
> Espelha o domínio do `jrny-service` (BE) — aqui o recorte é a **experiência do usuário**.

## 1. Intent

Ao final, **Marina (Head de Growth)** consegue abrir o Journey OS e **desenhar uma jornada** —
uma sequência de estágios ordenados (captura → nutrição → qualificação → oferta → fechamento) — e
**versionar as regras** que decidem para onde cada lead vai a seguir. **Rafael (Infoprodutor)**
**publica** a jornada quando a estratégia está pronta. **Lucas (SDR)** abre um lead e vê **em que
estágio ele está e por quê** — a trilha imutável de decisões de roteamento, com a regra que disparou,
o snapshot que a originou e se a IA assistiu. O FE JRNY transforma o motor de jornada e roteamento do
BE numa **superfície de autoria + auditoria explicável** — o funil deixa de ser implícito e passa a
ser um artefato governável.

## 2. Problem Statement

**Jornada atual:** depois que um lead é qualificado, o que acontece com ele vive em automações
desconexas de e-mail/WhatsApp. Não existe um modelo de "em que estágio o lead está e qual é o
próximo"; a decisão de "este lead quente vai direto para oferta, este frio volta para nutrição" é
feita na cabeça das pessoas ou em regras opacas de terceiros, sem versionamento. Quando um lead vai
para o caminho errado, ninguém consegue auditar qual regra disparou, com que dados, e se a IA
influenciou.

**Jornada nova (com o FE JRNY):**

- **Jornada como artefato** — Marina desenha estágios ordenados e tipados; a máquina de estados
  `RASCUNHO → PUBLICADA → ARQUIVADA` é visível e governável; editar uma jornada vigente = **nova versão**.
- **Roteamento governável** — regras versionadas (condição sobre score/segmento/atributo → estágio-alvo,
  com prioridade) listadas e editáveis; ativar/desativar é explícito e rastreável.
- **Decisão explicável** — abrir um lead mostra seu estágio corrente e a **trilha de decisões**: gatilho,
  regra disparada, alvo, **badge de assist IA**, motivo. O resultado do roteamento nunca aparece sem o "por quê".
- **Funil visível** — analytics de jornada (funil por estágio + telemetria de transições), read-only.

Sem o FE JRNY, o funil continuaria implícito e cada módulo a jusante (COMM/SALE) reagiria a sinais sem
que ninguém pudesse desenhar, versionar ou auditar a orquestração.

## 3. Personas

| Persona | Papel canônico | Job-to-be-done no FE JRNY |
|---|---|---|
| **Marina — Head de Growth** | `HEAD_GROWTH` | **Principal.** Desenha jornadas e estágios (Journey Builder), define e **versiona** regras de roteamento (Routing Engine), acompanha o funil. É quem mais tempo passa no builder e nas regras. |
| **Rafael — Infoprodutor / CEO** | `INFOPRODUTOR` | **Secundária**, **autoridade de publicação**: aprova/**publica**/arquiva jornadas (estratégia de funil). Cria nova versão de uma jornada publicada. |
| **Lucas — SDR / Closer** | `SDR` | **Terciária (leitura).** Abre um lead e vê seu **estágio corrente** + a **trilha de decisões** ("por que está aqui?"). Vê apenas o seu `data_scope`. Não edita jornadas/regras. |
| **Serviços do Journey OS** (LEAD, COMM, SALE, ASST) | — (máquina) | LEAD **dispara** roteamento (eventos); COMM/SALE **reagem** ao estágio; ASST **provê** o conteúdo referenciado — todos **fora** da UI JRNY. |

## 4. MVP Scope (in) — telas e fluxos

1. **Lista de jornadas** (`feature-journey-list`) — jornadas por estado (`RASCUNHO`/`PUBLICADA`/
   `ARQUIVADA`) + busca; criar rascunho; abrir o builder. Backed por `GET /journeys`.
2. **Journey Builder** (`feature-journey-builder`) — editar uma jornada `RASCUNHO`: estágios
   **ordenados e tipados**, adicionar/reordenar/remover; máquina de estados `publicar` / `arquivar` /
   `nova-versão`. Jornada `PUBLICADA` é **read-only** (edição só via nova versão).
3. **Editor de estágio** (`feature-stage-editor`) — editar um estágio: `tipoEstagio`
   (`CAPTURA`…`POS_VENDA`), nome, `assetRefId` (conteúdo publicado de ASST), `terminal`, `config`.
   Validações espelham o BE (`tipo-invalido`, `ordem-duplicada`).
4. **Routing Engine / regras** (`feature-routing-engine`) — CRUD de `regra_roteamento` **versionadas**:
   condição (sobre score/segmento/atributo do lead), estágio origem→destino, prioridade; ativar/desativar.
   Editar uma regra **bumpa a versão** e mantém a anterior referenciável pelas decisões.
5. **Decision log** (`feature-decision-log`) — para um lead: **estado de jornada corrente**
   (`InscricaoJornada`) + **trilha imutável** de `decisao_roteamento` (gatilho, regra, alvo, **assist IA**,
   motivo, `SEM_MUDANCA`/`NAO_ROTEADO` inclusos). Read-only.
6. **Journey analytics** (`feature-journey-analytics`, read-only) — funil por estágio + telemetria de
   transições (`journey-events`); saúde do roteamento (% de decisões com assist IA).
7. **Guards** — todas as rotas são pós-contexto: `authGuard` + `empresaGuard` + `accessGuard('jrny.*')`.

## 5. Out of Scope (MVP)

- **Canvas drag-and-drop livre estilo BPMN** — MVP é **editor estruturado de estágios ordenados**
  (lista/stepper com reordenação), não um canvas de grafo arbitrário (ver `ADR-005`).
- **Execução** das ações de estágio — envio de mensagem é da **COMM**, criação de oportunidade é da
  **SALE**. JRNY **decide e sinaliza**; a UI não executa efeito de canal/venda.
- **Comando "rotear este lead agora"** — não há endpoint de execução de roteamento; roteamento é
  **assíncrono**, disparado por eventos de LEAD. A UI **não** tem botão de roteamento manual.
- **Editor visual de condições** de regra — MVP usa formulário estruturado + expressão validada
  (espelha a gramática de snapshot do BE), não um query-builder visual livre.
- **A/B testing** de jornadas/variantes de roteamento.
- **Agendamento por tempo / delays complexos** (esperas, janelas) — MVP é dirigido por evento.
- **ML próprio de roteamento** — a inteligência vem da TechLab AI `orchestration` (BE-side, opcional).

## 6. Architectural Principles

1. **Decisão explicável, nunca caixa-preta (FE)** — toda exibição de decisão de roteamento mostra
   gatilho + regra (versão) + alvo + **badge assist IA** + motivo (ver `ADR-005`).
2. **Decide e sinaliza, não executa** — a UI desenha (jornadas/estágios/regras) e lê (estado +
   decisões); nunca dispara mensagem/oferta nem roteia manualmente.
3. **Standalone-first** nas features; **Signals-first** no estado de UI (sem NgRx — `ADR-002`);
   **Lazy-by-default** (entry como library — `ADR-003`); **OnPush** obrigatório; NgModule só no entry lazy.
4. **module-pattern canônico** — slicing de libs por módulo idêntico aos demais (ver `ADR-001`).
5. **IA é assist BE-side, refletido — não chamado** — o FE nunca conhece a TechLab AI; só reflete
   `assistIa` e degrada visualmente (badge "roteamento determinístico").
6. **Imutabilidade do publicado** — jornada `PUBLICADA` é read-only na UI; edição = nova versão;
   estágios/regras só editáveis em `RASCUNHO` (espelha `409 transicao-invalida`).
7. **Isolamento por empresa** — troca de empresa invalida jornadas/builder em tela antes de carregar os
   da nova empresa; nenhum dado cross-empresa.
8. **Integração com o Shell via module registry** — descriptor + `ModuleShellIntegrationService`
   (ver `ADR-004`); JRNY não conhece o Shell diretamente.

## 7. Success Signals

- Marina desenha uma jornada de 5 estágios e Rafael a **publica** sem sair da UI; a máquina de estados
  (`RASCUNHO → PUBLICADA`) é clara e a publicação sem estágio é bloqueada com mensagem útil
  (espelha `422 jrny.jornada.sem-estagio`).
- Editar uma jornada `PUBLICADA` oferece **criar nova versão** em vez de quebrar — a versão vigente e as
  inscrições ativas nunca mudam embaixo do lead (espelha `nova-versao` / `409 transicao-invalida`).
- Lucas abre um lead e responde "**por que** está neste estágio?" — vê a regra disparada, o snapshot e o
  badge de assist IA, sempre; decisões `SEM_MUDANCA`/`NAO_ROTEADO` também aparecem.
- Indisponibilidade da IA não quebra a UI: a decisão aparece com badge **neutro** ("roteamento
  determinístico"), nunca como erro/toast.
- Trocar de empresa nunca mostra jornada/regra/decisão da empresa anterior (cross-empresa guard de UI).
- Reordenar estágios e ativar/desativar regras reflete na UI de forma rastreável (versão da regra
  destacada; decisões antigas continuam referenciando a versão que as produziu).
- Métricas Web Vitals dentro do orçamento: TTI < 3s, CLS < 0.1, FID/INP saudáveis; bundle lazy do JRNY
  dentro do limite do módulo (sem lib de canvas pesada no MVP — `ADR-005`).
- 100% dos cenários do SPEC-08 viram spec Playwright descobrível (gate A5 e2e-validate).

---

## Referências

- ADRs: `adr/ADR-001..005`
- Brief: `../_brief.md`
- Blueprint: `02-architecture-blueprint.md`
- BE (espelho): `docs/architecture/backend/services/jrny-service/{01,03}-*.md` + `contracts/api-contract.md`
- Multi-tenancy / Access Layer: `docs/architecture/frontend/standards/access-layer-contracts.md`
- module-pattern: `docs/architecture/frontend/standards/module-pattern.md`
