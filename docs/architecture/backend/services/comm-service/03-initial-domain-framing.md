# 03 — Initial Domain Framing — COMM (Communication Hub)

> Rascunho de domínio (refinado em `/be-architect-specs` → `contracts/data-model.md`).
> Linguagem ubíqua em pt-BR (identificadores canônicos), alinhada ao padrão WRKS/ASST.

## 1. Ubiquitous Language

| Termo | Definição |
|---|---|
| **Template** (`template_mensagem`) | Modelo reutilizável de mensagem, tipado por `canal` e `tipo`, com corpo contendo placeholders `{{variavel}}`. Agregado raiz. Pode referenciar um asset publicado do ASST como fonte. |
| **Canal** (`canal`) | Meio de comunicação: `WHATSAPP`, `EMAIL`, `TELEGRAM`, `SMS`. O domínio conhece o canal; o provedor concreto vive no adapter. |
| **Tipo de template** (`tipo_template`) | Natureza da mensagem: `TRANSACIONAL`, `MARKETING`, `NOTIFICACAO`. |
| **Template Studio** | Capacidade de composição/edição assistida por IA (TechLab AI `document_composition`). Produz rascunho de corpo de template. |
| **Mensagem** (`mensagem`) | Instância de **disparo** a um destinatário por um canal. Agregado raiz. Carrega o `conteudo_renderizado` imutável (snapshot do que foi enviado) e o estado de entrega. |
| **Destinatário** (`ReferenciaDestinatario`) | Quem recebe: referência ao lead + endereço resolvido (telefone/e-mail/chatId) + preferência de canal. |
| **Estado de entrega** (`estado_entrega`) | Posição na máquina de entrega: `PENDENTE`, `ENFILEIRADA`, `ENVIADA`, `ENTREGUE`, `LIDA`, `FALHADA`. |
| **Evento de entrega** (`evento_entrega`) | Registro **append-only** de uma transição do ciclo de vida da mensagem (alimenta `communication-events`). |
| **Regra de roteamento** (`regra_roteamento`) | Regra priorizada que resolve canal preferido + fallback e template a partir de condições (segmento/estágio/preferência/janela). |
| **Config de canal** (`config_canal`) | Configuração por empresa de um canal: provedor, identidade de remetente e **referência** de credencial. |
| **Chave de idempotência** (`chave_idempotencia`) | Identificador do disparo fornecido/derivado pelo solicitante; impede envio duplicado ao provedor. |
| **Empresa** | Tenant (workspace). Define o schema operacional `emp_<slug>`. |

## 2. Aggregates and Entities (rascunho inicial)

- **Template** *(agregado raiz)* — `id`, `empresa_id`, `nome`, `canal`, `tipo_template`, `assunto` (nullable, e-mail), `corpo` (texto/HTML com placeholders), `variaveis[]` (placeholders declarados), `asset_origem_id` (nullable → ASST), `estado` (`RASCUNHO`/`ATIVO`/`ARQUIVADO`), `versao` (int), `criado_em`, `atualizado_em`.
- **Mensagem** *(agregado raiz — disparo)* — `id`, `empresa_id`, `template_id` (nullable; disparo ad-hoc permitido), `canal`, `destinatario` (`ReferenciaDestinatario`), `conteudo_renderizado` (snapshot imutável), `estado_entrega`, `provedor`, `provedor_message_id` (nullable), `tentativas` (int), `motivo_falha` (nullable), `chave_idempotencia` (unique por empresa), `agendado_para` (nullable), `criado_em`, `atualizado_em`.
  - **EventoEntrega** *(entidade filha, append-only)* — `id`, `mensagem_id`, `tipo` (`ENFILEIRADA`/`ENVIADA`/`ENTREGUE`/`LIDA`/`FALHADA`/`REJEITADA`), `provedor_payload` (jsonb — callback bruto), `ocorrido_em`.
- **RegraRoteamento** *(agregado raiz)* — `id`, `empresa_id`, `nome`, `prioridade` (int), `condicoes` (jsonb — segmento/estágio/preferência/janela), `canal_preferido`, `canais_fallback[]`, `template_id` (nullable), `ativa` (bool), `criado_em`.
- **ConfigCanal** *(agregado/config)* — `id`, `empresa_id`, `canal`, `provedor` (`META_WABA`/`SES`/`SENDGRID`/`TELEGRAM_BOT`/`TWILIO`/`SNS`), `identidade_remetente`, `credencial_ref` (ponteiro p/ secret), `ativo` (bool), `janela_envio` (jsonb opcional — quiet hours/rate).
- **Value objects:** `ReferenciaDestinatario` (leadId, nome, endereco, canalPreferencia), `ConteudoRenderizado` (texto final + variáveis aplicadas), `BriefComposicao` (prompt/contexto enviado à TechLab AI), `ResultadoEnvio` (provedorMessageId, status, erro).

> Agregado consistente: `Mensagem` controla suas `EventoEntrega` e suas transições de estado; o
> domínio nunca conhece o provedor concreto — só `canal` (o adapter resolve o provedor).

## 3. Domain Events (inicial)

| Evento | Quando | Payload (resumo) |
|---|---|---|
| `journey-os.mensagem.enfileirada` | Disparo aceito e enfileirado | `mensagemId`, `empresaId`, `canal`, `leadId`, `templateId` |
| `journey-os.mensagem.enviada` | **Evento-âncora** — entregue ao provedor do canal | `mensagemId`, `empresaId`, `canal`, `provedor`, `leadId`, `provedorMessageId` |
| `journey-os.mensagem.entregue` | Provedor confirma entrega (webhook) | `mensagemId`, `empresaId`, `canal`, `entregueEm` |
| `journey-os.mensagem.falhada` | Falha após retries / rejeição do provedor | `mensagemId`, `empresaId`, `canal`, `motivo` |

> `journey-os.mensagem.lida` (read receipt) é opcional no MVP — emitido quando o canal suporta
> recibo de leitura.

Consumidos: `journey-os.modelo.acesso.alterado` (WRKS — invalida cache de AccessDecision),
`journey-os.empresa.provisionada` (WRKS — seed de canais/templates default),
`journey-os.asset.versao.publicada` (ASST — sinaliza template vinculado para revisão),
`journey-os.lead.segmento.alterado` (LEAD — reavalia audiência/roteamento).

## 4. State Transitions (alto nível)

```
                 enfileirar              enviar (provedor OK)        webhook            webhook
   (∅) ──────────► PENDENTE ───────────► ENFILEIRADA ─────────────► ENVIADA ─────────► ENTREGUE ──────► LIDA
                                              │                        │
                                              │  falha/rejeição        │ falha tardia (bounce)
                                              ▼                        ▼
                                          FALHADA ◄────────────────────┘
```

- Só `ENFILEIRADA` pode ir a `ENVIADA` ou `FALHADA`. `ENVIADA` pode ir a `ENTREGUE`/`FALHADA` (bounce tardio); `ENTREGUE` pode ir a `LIDA`.
- Transições são **monotônicas** (sem regressão); cada transição grava um `EventoEntrega` (append-only).
- `FALHADA` é terminal (reprocesso = nova `Mensagem`, preservando a trilha da original).

## 5. Invariants

1. `conteudo_renderizado` é **imutável** após o envio — proveniência do que a pessoa efetivamente recebeu.
2. Idempotência: a mesma `chave_idempotencia` (por empresa) nunca gera dois envios ao provedor; segundo pedido retorna a `Mensagem` existente.
3. Transição de `estado_entrega` só pelo agregado raiz e apenas se válida pela máquina de estados (transição inválida → erro de domínio, nunca estado corrompido); transições são monotônicas.
4. Roteamento sempre resolve um canal (preferido ou fallback) **ou** falha explicitamente — nunca envio silencioso para canal inexistente/sem config.
5. Só template em estado `ATIVO` pode ser usado para envio real (RASCUNHO só para teste/preview).
6. `empresa_id` de todo registro = `EmpresaContextHolder.require()` (zero cross-empresa).
7. Segredo de provedor **nunca** persistido em claro — `config_canal` guarda apenas `credencial_ref`.
8. Conteúdo composto pela IA é sempre rastreável à `origem` + `briefComposicao` (proveniência/auditoria).

---

## Referências

- `02-architecture-blueprint.md` · `05-persistence-model.md`
- `adr/ADR-005-channel-adapter-pattern.md` (adapters de canal) · `adr/ADR-003-messaging-strategy.md`
- `docs/architecture/integrations/techlab-ai-integration.md` (`document_composition`)
