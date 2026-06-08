# 01 — Architectural Vision — COMM (Communication Hub) · Frontend

> Camada de visão FE (Layer 1 — Architect). Gera contratos de UI, não código.
> Módulo: **COMM** · module `comm` · app lazy `apps/comm` · consome `comm-service` (`/api/v1`).

## 1. Intent

Ao final, Marina (Head de Growth) e Lucas (SDR) têm **um único lugar** para falar com leads de
forma padronizada e rastreável. A UI do COMM permite **catalogar e editar templates** versionados
(com placeholders `{{variavel}}` e composição assistida pelo **Template Studio**), **definir regras
de roteamento** que escolhem o canal certo, **disparar** mensagens de forma idempotente e
**acompanhar o ciclo de vida** de cada mensagem (enviada → entregue → lida → falhada) em tempo quase
real, além de **configurar canais/provedores** por empresa. O FE abstrai totalmente os provedores
(nunca conhece Meta/Twilio/SES) — fala apenas em termos de **canal** — e delega 100% da IA ao BE.

## 2. Problem Statement

A comunicação hoje é fragmentada e cega:

| Jornada atual (sem COMM) | Jornada nova (com a UI COMM) |
|---|---|
| Copy improvisada a cada disparo, sem versão aprovada nem reuso. | Catálogo de **templates versionados** com estado `RASCUNHO → ATIVO → ARQUIVADO` e editor com placeholders validados. |
| "Mando WhatsApp ou e-mail?" decidido no improviso. | **Regras de roteamento** explícitas (canal preferido + fallback por segmento/estágio/preferência), auditáveis. |
| Disparou e sumiu: ninguém sabe se entregou/foi lido. | **Timeline de entrega** por mensagem (`ENFILEIRADA → ENVIADA → ENTREGUE → LIDA`/`FALHADA`) atualizada em tempo quase real. |
| Cliques duplos viram mensagens duplicadas. | Disparo **idempotente** (a UI envia `Idempotency-Key`; replay não duplica). |
| Escrever a primeira versão da copy é gargalo. | **Template Studio**: IA compõe um rascunho a partir de brief + contexto (com degradação graciosa). |
| Credenciais de provedor espalhadas/inseguras. | **Config de canal** por empresa guardando só a **referência** da credencial (nunca o segredo). |

## 3. Personas

| Persona | Papel canônico | Job-to-be-done na UI COMM |
|---|---|---|
| **Marina — Head de Growth** | `HEAD_GROWTH` | Persona **principal**. Cria/edita templates (e usa o Template Studio), define regras de roteamento, acompanha entregabilidade do catálogo de mensagens. |
| **Lucas — SDR / Closer** | `SDR` | Persona **secundária**. Dispara mensagens 1:1 para leads da sua fila; acompanha `ENVIADA → ENTREGUE → LIDA`; `data_scope` restringe quais leads/mensagens ele enxerga. |
| **Rafael — Infoprodutor / CEO** | `INFOPRODUTOR` | Configura canais (provedor, identidade de remetente, `credencialRef`) e padrões de comunicação. |
| **Serviços do Journey OS** (JRNY, SALE, LEAD) | — (máquina) | **Acionam** disparo via API BE (estágio de jornada, notificação de oferta, gatilho de qualificação). **Não** usam a UI COMM. |

## 4. MVP Scope (in) — telas / fluxos / formulários

1. **Catálogo de templates** (`/comm/templates`): lista paginada por `canal`/`tipo`/`estado` com filtros + busca (`q`); criar novo template.
2. **Editor de template** (`/comm/templates/:id`): editar `nome`, `assunto` (obrigatório p/ EMAIL), `corpo` com placeholders `{{variavel}}` + lista de `variaveis` declaradas (validação síncrona: toda placeholder usada deve estar declarada); vínculo opcional a asset publicado; ações de estado **Ativar** (`RASCUNHO→ATIVO`) e **Arquivar**.
3. **Template Studio** (`/comm/templates/:id/studio`): formulário de brief + contexto → compõe corpo via IA → preenche um rascunho para revisão (nunca ativa sozinho); degradação graciosa quando a IA cai.
4. **Regras de roteamento** (`/comm/routing-rules`): lista ordenada por prioridade; criar/editar regra (condições, `canalPreferido`, `canaisFallback`, `templateId`, `prioridade`, `ativa`).
5. **Disparo de mensagem** (ação em `/comm/messages` ou no detalhe do lead): formulário de disparo 1:1 (template ATIVO + `leadId` + `variaveis`); envia com `Idempotency-Key`.
6. **Histórico + rastreio de mensagens** (`/comm/messages`, `/comm/messages/:id`): lista/busca por lead/canal/estado/período; detalhe com **timeline do ciclo de vida** (eventos cronológicos) atualizada por polling.
7. **Configuração de canais** (`/comm/channels`): lista de canais configurados (com `credencialRef` mascarada); criar/editar config (`canal`, `provedor`, `identidadeRemetente`, `credencialRef`, janela de envio).
8. **Guards de acesso**: todas as rotas exigem `authGuard` + `empresaGuard` + `accessGuard('comm.*')`.

## 5. Out of Scope (MVP)

- Caixa de entrada unificada / chat bidirecional em tempo real (inbox, 2-way, chatbot).
- Campaign manager avançado (A/B testing, cadências complexas com ramificação) — fora do MVP FE.
- Editor visual de e-mail (drag-and-drop / WYSIWYG rico) — MVP é editor de texto/HTML com placeholders.
- Gestão legal completa de opt-in/opt-out (double opt-in, supressão regulatória).
- Roteamento por custo (least-cost) entre múltiplos provedores do mesmo canal.
- Deliverability scoring / warm-up de domínio / reputação de IP.
- Hospedagem própria de mídia — binários referenciados por URL.
- UI de webhooks — callbacks de provedor são server-to-server (sem tela).

## 6. Architectural Principles

1. **Standalone-first** nas features; **OnPush** obrigatório em todo componente.
2. **Signals-first** — estado de UI em `signal<T>` privado + `.asReadonly()` nas facades; **sem NgRx** (ADR-002).
3. **Lazy-by-default** — entry do módulo como library `@journeyos/comm` (`libs/comm/shell-entry`), carregada pelo Shell via `loadChildren` (ADR-003/004); features via `loadComponent`.
4. **IA é capacidade delegada** — o Template Studio chama **somente** o `comm-service`; o FE nunca conhece a TechLab AI. Falha da IA **degrada apenas o Studio** (CRUD/roteamento/disparo/rastreio intactos).
5. **Provedor é detalhe do BE** — o FE fala apenas em `canal`; nunca conhece Meta/Twilio/SES/Telegram. Config de canal nunca expõe segredo (só `credencialRef`).
6. **Disparo idempotente** — a UI envia `Idempotency-Key`; replay/duplo-clique nunca gera dois envios.
7. **Rastreio é quase-tempo-real por polling** — sem endpoint de streaming no BE; a UI faz polling com backoff enquanto a mensagem está em estado não-terminal (ADR-005).
8. **Multi-empresa isolado** — todo dado é escopado pela empresa ativa; troca de empresa invalida o que está em tela (sem vazamento cross-empresa — LGPD).

## 7. Success Signals

- Marina compõe um template de boas-vindas no Template Studio em < 1 min (brief → rascunho), em vez de partir da folha em branco.
- Uma regra de roteamento mostra deterministicamente "WhatsApp (preferido) → e-mail (fallback)" e é auditável na UI.
- Lucas dispara para um lead e vê o status mudar `ENVIADA → ENTREGUE → LIDA` em tempo quase real (timeline atualizando por polling).
- Duplo clique em "Enviar" (mesma `Idempotency-Key`) produz **um** envio — a UI reflete a mensagem existente, sem duplicar.
- TechLab AI indisponível: catálogo, edição, roteamento e disparo continuam funcionando; só o Template Studio mostra degradação explícita.
- Nenhuma tela da empresa A mostra template/mensagem/regra/canal da empresa B (cross-empresa guard).
- Métricas web do shell de COMM dentro do alvo: TTI < 3.5 s, CLS < 0.1, FID/INP saudáveis; p95 de chamada de catálogo < 800 ms.
- 100% dos cenários do SPEC-08 (e2e) cobrem os fluxos golden + degradação + isolamento.

---

## Referências

- ADRs: `adr/ADR-001..005`
- Brief: `_brief.md`
- Blueprint: `02-architecture-blueprint.md`
- BE vision/domínio: `docs/architecture/backend/services/comm-service/{01,03}-*.md`
- BE API: `docs/architecture/backend/services/comm-service/contracts/api-contract.md`
- TechLab AI: `docs/architecture/integrations/techlab-ai-integration.md`
