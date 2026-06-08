# 01 — Architectural Vision — JRNY (Journey & Routing)

> Camada de visão (Layer 1 — Architect). Gera contratos, não código.
> Módulo: **JRNY** · serviço `jrny-service` · pacote `com.journeyos.jrny`.

## 1. Intent

JRNY é o **motor de jornada e roteamento** do Journey OS. Centraliza o desenho de jornadas
multi-estágio (**Journey Builder**), a decisão de **para onde cada lead vai a seguir**
(**Routing Engine**) e o registro auditável de **por que** cada decisão foi tomada (**decision
log**). É a peça que transforma o sinal de qualificação produzido por LEAD em movimento
estruturado pelo funil — captura → nutrição → qualificação → oferta → fechamento — acionando
COMM (mensageria) e SALE (oportunidade) nos momentos certos, com conteúdo publicado por ASST. A
inteligência de recomendação é **delegada à TechLab AI** (`orchestration`) e é sempre opcional:
o roteamento determinístico é a base, a IA apenas o aprimora.

## 2. Problem Statement

A persona de growth (Marina) qualifica leads, mas o "depois" é caótico: cada lead deveria
percorrer uma jornada coerente, e hoje isso vive em automações desconexas de e-mail/WhatsApp.
As dores concretas:

- **Sem visão de jornada** — não existe um modelo de "em que estágio o lead está e qual é o próximo"; o funil é implícito, espalhado em ferramentas.
- **Roteamento ad-hoc** — a decisão de "este lead quente vai direto para oferta, este frio volta para nutrição" é feita na cabeça das pessoas ou em regras opacas de terceiros, sem versionamento.
- **Sem trilha de decisão** — quando um lead vai para o caminho errado, ninguém consegue auditar qual regra disparou, com que dados, e se a IA influenciou.
- **Reação lenta a sinais** — quando o score de um lead muda (LEAD), nada reavalia automaticamente seu posicionamento na jornada.

O Journey OS resolve isso com um motor que trata a **jornada** como artefato versionado, o
**roteamento** como decisão determinística (regras versionadas) opcionalmente assistida por IA,
e o **decision log** como trilha imutável — sinalizando para COMM/SALE agir, sem executar a
ação ele mesmo.

## 3. Personas

| Persona | Papel canônico | Relação com JRNY |
|---|---|---|
| **Marina — Head de Growth** | `HEAD_GROWTH` | Persona **principal**. Desenha jornadas e estágios, define regras de roteamento, acompanha o funil. |
| **Rafael — Infoprodutor / CEO** | `INFOPRODUTOR` | Persona **secundária**, **autoridade de publicação** da jornada: aprova/publica a estratégia de funil. |
| **Lucas — SDR / Closer** | `SDR` | Consumidor de leitura: vê em que estágio cada lead está e por quê; `data_scope` restringe o que enxerga. |
| **Serviços do Journey OS** (LEAD, COMM, SALE, ASST) | — (máquina) | LEAD **dispara** roteamento (eventos); COMM/SALE **reagem** ao estágio (Feign + evento); ASST **provê** conteúdo publicado referenciado nos estágios. |

## 4. MVP Scope (in)

1. **Journey Builder**: agregado `jornada` com `estagio[]` ordenados, tipados (`CAPTURA`, `NUTRICAO`, `QUALIFICACAO`, `OFERTA`, `FECHAMENTO`, `POS_VENDA`) no schema `emp_<slug>`; máquina de estados `RASCUNHO → PUBLICADA → ARQUIVADA`.
2. **Routing Engine**: `regra_roteamento` versionadas (condições sobre score/segmento/atributo do lead) avaliadas a cada evento de domínio; decisão do estágio/jornada-alvo; matrícula (`inscricao_jornada`) e avanço do lead.
3. **Decision log**: `decisao_roteamento` **imutável** — snapshot de entrada, regra disparada, alvo escolhido, flag de assist de IA, motivo; projetado no índice Elastic `routing-decisions` (fact).
4. **Orchestration assist (TechLab AI)**: recomendação de próximo-melhor-estágio via capability `orchestration`, **opcional**; degrada para roteamento determinístico em falha/timeout.
5. **Telemetria de jornada**: cada transição emite evento de domínio e alimenta o índice Elastic `journey-events` (fact).
6. **Consumo de conteúdo**: estágios referenciam assets publicados de ASST (Feign `AssetQueryClient`); atualização reativa por `asset.versao.publicada`.
7. **Consumo cross-módulo (leitura)**: estado de jornada do lead exposto via Feign (`JourneyQueryClient`) + eventos `lead.roteado` / `estagio.transicionado` para COMM/SALE.

## 5. Out of Scope (MVP)

- Editor visual drag-and-drop do Journey Builder — o MVP expõe API/modelo; o canvas é responsabilidade do FE / pós-MVP.
- Ramificação condicional arbitrária estilo BPMN completo — MVP é estágios ordenados + regras de salto, não um motor de workflow genérico.
- A/B testing de jornadas / variantes de roteamento.
- Agendamento por tempo e delays complexos (esperas, janelas) — MVP é dirigido por evento; delays simples são pós-MVP.
- **Execução** das ações de estágio — envio de mensagem é da **COMM**, criação de oportunidade é da **SALE**. JRNY **decide e sinaliza**, não executa.
- Modelo de machine-learning próprio de roteamento — a inteligência vem da TechLab AI `orchestration`.

## 6. Architectural Principles

1. **Hexagonal estrito** — domínio sem Spring/JPA; portas in/out; ArchUnit bloqueante (ver `ADR-001`).
2. **Determinístico primeiro, IA depois** — o Routing Engine decide com regras versionadas; a TechLab AI (`orchestration`) é **assist opcional** e nunca caminho crítico. IA fora do ar → roteamento determinístico decide sozinho (fallback graceful — ver `ADR-003`/`ADR-005`).
3. **Toda decisão é auditável** — cada roteamento grava uma `decisao_roteamento` imutável com o snapshot que a originou e a regra/assist que a produziu. Decisão sem trilha é proibida por construção (ver `ADR-005`).
4. **JRNY decide, não executa** — emite eventos/sinais; COMM e SALE executam. Sem acoplamento síncrono ao efeito colateral.
5. **Isolamento por schema** — JRNY opera exclusivamente no `emp_<slug>` do tenant corrente; zero vazamento cross-empresa (ver `ADR-004`).
6. **Roteamento é dirigido por evento** — `lead.qualificado`/`score.atualizado`/`segmento.alterado` disparam reavaliação; o sistema reage a sinais, não a polling.
7. **Elastic não é fonte da verdade** — `journey-events`/`routing-decisions` aceleram analytics/auditoria; o PostgreSQL continua sendo a fonte canônica do estado de jornada.
8. **Jornada publicada é imutável em runtime** — alterar uma jornada vigente = nova versão; inscrições ativas não mudam de definição embaixo do lead (ver `ADR-005`).

## 7. Success Signals

- Marina publica uma jornada de 5 estágios e, ao qualificar um lead (LEAD), ele é matriculado e roteado automaticamente em < 5 s — sem intervenção manual.
- Quando o score de um lead muda, o Routing Engine reavalia e, se uma regra dispara, reroteia o lead — com `decisao_roteamento` registrada.
- Para qualquer lead, é possível responder "por que ele está neste estágio?" recuperando a decisão (regra disparada, dados de entrada, se a IA assistiu) — sempre.
- TechLab AI indisponível: o roteamento continua funcionando deterministicamente; nenhuma decisão é bloqueada por falha de IA.
- COMM/SALE reagem ao evento `lead.roteado` para agir no estágio, sem conhecer o motor interno de JRNY.
- Nenhuma requisição com JWT da empresa A retorna jornada/decisão da empresa B (cross-empresa guard).
- 100% das cláusulas SHALL das specs viram cenário BDD (gate D-218).

---

## Referências

- ADRs: `adr/ADR-001..005`
- Brief: `_brief.md`
- Blueprint: `02-architecture-blueprint.md`
- Multi-tenancy global: `docs/architecture/shared/multi-empresa.md`
- TechLab AI: `docs/architecture/integrations/techlab-ai-integration.md`
- Elastic (`journey-events`, `routing-decisions`): `docs/architecture/integrations/elastic-data-contract.md`
