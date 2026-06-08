# 01 — Architectural Vision — COMM (Communication Hub)

> Camada de visão (Layer 1 — Architect). Gera contratos, não código.
> Módulo: **COMM** · serviço `comm-service` · pacote `com.journeyos.comm`.

## 1. Intent

COMM é o **hub de comunicação multicanal** do Journey OS. Centraliza tudo que diz respeito a
falar com leads e clientes — **templates** de mensagem versionados, **regras de roteamento** que
escolhem o canal certo, **disparo** padronizado e idempotente através de WhatsApp, e-mail,
Telegram e SMS, e o **rastreio do ciclo de vida** de cada mensagem (enviada, entregue, lida,
falhada). COMM **abstrai os provedores** de cada canal atrás de adapters (o domínio nunca conhece
Meta/Twilio/SES) e **delega à TechLab AI** a composição assistida de copy. Uma mensagem enviada
por COMM é o ponto onde a estratégia do Journey OS (jornada, oferta, qualificação) vira contato
real com a pessoa.

## 2. Problem Statement

A persona de growth (Marina) e o SDR (Lucas) precisam falar com leads no momento e no canal
certos, mas a comunicação hoje é fragmentada e cega:

- **Sem template padronizado** — cada disparo é copy improvisada; não há versão aprovada, reuso nem consistência de marca.
- **Sem decisão de canal** — "mando WhatsApp ou e-mail?" é decidido no improviso, sem regra por segmento/estágio/preferência do lead.
- **Sem rastreio** — disparou e sumiu: ninguém sabe se entregou, se foi lido, se falhou. Atribuição (SALE) e avanço de jornada (JRNY) ficam sem sinal confiável.
- **Sem idempotência** — reprocessos e cliques duplos viram mensagens duplicadas para o lead.
- **Produção lenta de copy** — escrever a primeira versão de uma mensagem do zero é gargalo; a IA poderia compor um rascunho a partir de um brief + contexto da empresa.

O Journey OS resolve isso com um hub que trata cada disparo como uma **mensagem rastreável**,
renderizada de um **template versionado**, roteada por **regra explícita** e entregue por um
**adapter de canal** provedor-agnóstico — emitindo eventos de domínio a cada transição do ciclo
de vida.

## 3. Personas

| Persona | Papel canônico | Relação com COMM |
|---|---|---|
| **Marina — Head de Growth** | `HEAD_GROWTH` | Persona **principal**. Cria/edita templates (e usa o Template Studio), define regras de roteamento e sequências, acompanha entregabilidade. |
| **Lucas — SDR / Closer** | `SDR` | Persona **secundária**. Dispara mensagens 1:1 para leads da sua fila; vê status de entrega/leitura; `data_scope` restringe quem ele enxerga. |
| **Rafael — Infoprodutor / CEO** | `INFOPRODUTOR` | Configura canais (provedores, identidade de remetente), define padrões de comunicação e limites. |
| **Serviços do Journey OS** (JRNY, SALE, LEAD) | — (máquina) | **Acionam** COMM para falar com o lead (estágio de jornada, notificação de oferta, gatilho de qualificação) via API/eventos. |

## 4. MVP Scope (in)

1. **Template CRUD + catálogo**: `template_mensagem` tipado por `canal` (`WHATSAPP`, `EMAIL`, `TELEGRAM`, `SMS`) e `tipo` (`TRANSACIONAL`, `MARKETING`, `NOTIFICACAO`); corpo com placeholders `{{variavel}}`; estado `RASCUNHO → ATIVO → ARQUIVADO`; vínculo opcional a um asset publicado do ASST como fonte de conteúdo.
2. **Template Studio**: `POST /api/v1/templates/{id}/studio/compose` → compõe/edita copy via TechLab AI `document_composition` a partir de brief + contexto da empresa; resultado vira novo conteúdo de template em `RASCUNHO`.
3. **Roteamento**: `regra_roteamento` resolve **canal preferido + fallback** e template a partir de condições (segmento do lead, estágio da jornada, preferência de canal, janela de envio); prioridade entre regras.
4. **Disparo multicanal**: `mensagem` renderizada de template + variáveis, enviada via **adapter de canal** (provedor-agnóstico) com **idempotência por chave**; snapshot imutável do conteúdo efetivamente enviado.
5. **Máquina de entrega**: `PENDENTE → ENFILEIRADA → ENVIADA → ENTREGUE → LIDA` (+ `FALHADA`), com `evento_entrega` append-only alimentado por callbacks (webhooks) do provedor.
6. **Rastreio/analytics**: projeção do ciclo de vida no índice Elastic `communication-events` (fact); consulta de status por mensagem/lead.
7. **Config de canal por empresa**: `config_canal` com provedor + identidade de remetente + **referência** de credencial (secret manager), nunca o segredo em claro.

## 5. Out of Scope (MVP)

- Caixa de entrada unificada / conversas bidirecionais em tempo real (inbox, 2-way chat, chatbot).
- Campaign manager avançado com A/B testing e cadências complexas (sequência simples sim; orquestração avançada não).
- Editor visual de e-mail (drag-and-drop) — MVP é template texto/HTML com placeholders.
- Gestão legal completa de opt-in/opt-out (double opt-in, supressão regulatória) — MVP registra consentimento básico.
- Roteamento por custo entre múltiplos provedores do mesmo canal (least-cost routing).
- Deliverability scoring / warm-up de domínio / reputação de IP.
- Hospedagem própria de mídia — binários (imagens/anexos) **referenciados por URL** (como no ASST).

## 6. Architectural Principles

1. **Hexagonal estrito** — domínio sem Spring/JPA; portas in/out; ArchUnit bloqueante (ver `ADR-001`).
2. **Provedor é detalhe de adapter** — o domínio conhece apenas `canal`; cada provedor (Meta/Twilio/SES/Telegram) vive atrás de um adapter sob o port `CanalEnvioPort`. Adicionar canal = novo adapter, **sem** tocar o domínio (ver `ADR-005`).
3. **IA é capacidade delegada** — toda composição de copy passa pela TechLab AI via HTTP; o BE **nunca** chama provider de IA direto. TechLab AI fora do ar degrada o Template Studio, não o CRUD/roteamento/disparo (fallback graceful — ver `ADR-003`).
4. **Isolamento por schema** — COMM opera exclusivamente no `emp_<slug>` do tenant corrente; zero vazamento cross-empresa (ver `ADR-004`).
5. **Disparo é idempotente** — a mesma `chave_idempotencia` nunca gera dois envios ao provedor; reprocessos e retries são seguros por construção.
6. **O que foi enviado é imutável** — `conteudo_renderizado` é congelado no momento do envio (proveniência: sabemos exatamente o que a pessoa recebeu).
7. **Cada transição é um evento de domínio** — enfileirada/enviada/entregue/falhada emitem evento; consumidores (JRNY/SALE/INTL) reagem sem acoplamento síncrono.
8. **Busca/analytics não são fonte da verdade** — Elastic (`communication-events`) acelera análise; se cair, o PostgreSQL continua sendo a fonte canônica do ciclo de vida.

## 7. Success Signals

- Marina compõe um template de boas-vindas no Template Studio em < 1 min (brief → rascunho), em vez de partir da folha em branco.
- Uma regra de roteamento escolhe deterministicamente WhatsApp (preferido) e cai para e-mail (fallback) quando o lead não tem WhatsApp — sempre auditável.
- Lucas dispara para um lead e vê o status mudar `ENVIADA → ENTREGUE → LIDA` em tempo quase real.
- Dois cliques no botão "enviar" (mesma `chave_idempotencia`) produzem **um** envio ao provedor, nunca dois.
- Enviar uma mensagem propaga `journey-os.mensagem.enviada` e registra o fato em `communication-events` em < 5 s.
- Nenhuma requisição com JWT da empresa A dispara/consulta mensagem da empresa B (cross-empresa guard).
- TechLab AI indisponível: CRUD de template, roteamento e disparo continuam funcionando (apenas o Template Studio retorna degradação explícita).
- 100% das cláusulas SHALL das specs viram cenário BDD (gate D-218).

---

## Referências

- ADRs: `adr/ADR-001..005`
- Brief: `_brief.md`
- Blueprint: `02-architecture-blueprint.md`
- Multi-tenancy global: `docs/architecture/shared/multi-empresa.md`
- TechLab AI: `docs/architecture/integrations/techlab-ai-integration.md`
- Elastic (`communication-events`): `docs/architecture/integrations/elastic-data-contract.md`
