# SPEC-03 — Channel Routing & Adapter Pattern (sub-feature)

> EARS guide linkado. Concretiza ADR-005. Relaciona SPEC-02 (dispatch), SPEC-10 (providers), SPEC-06 (config secrets).

## Objetivo

Especificar (a) como uma mensagem resolve canal + template a partir de regras priorizadas e (b)
como o disparo é executado de forma **provedor-agnóstica** através do port `CanalEnvioPort` com
um adapter por canal/provedor.

## Escopo

- **In:** avaliação de `regra_roteamento` (prioridade, condições, canal preferido + fallback); resolução de `config_canal` ativa; seleção do adapter por `(canal, provedor)`; normalização de callback por adapter.
- **Out:** máquina de entrega (SPEC-02); contrato fino de cada provedor (SPEC-10).

## Decisões técnicas

- **Roteamento:** regras avaliadas por `prioridade` ascendente; a primeira regra ativa cujas `condicoes` casam o contexto (segmento/estágio/preferência/janela) resolve `canal_preferido`; se o lead não tem endereço para o preferido, tenta os `canais_fallback` em ordem.
- **Falha explícita:** se nenhum canal resolve, o disparo falha com `422 comm.roteamento.sem-canal` (nunca envio silencioso).
- **Port único `CanalEnvioPort`** (`application/port/out`): `ResultadoEnvio enviar(Mensagem, ConfigCanal)`. O domínio conhece só `Canal` (enum).
- **Adapters** (`infrastructure/channels`): `WhatsAppEnvioAdapter`, `EmailEnvioAdapter`, `TelegramEnvioAdapter`, `SmsEnvioAdapter`. Um `CanalEnvioRouter` (factory) seleciona o adapter por `(canal, config.provedor)` em runtime.
- **Aditivo:** novo canal/provedor = novo adapter + `config_canal`, sem tocar domínio/roteamento (Open/Closed).
- **Segredos:** adapter resolve `config_canal.credencial_ref` no secret manager; nunca em claro.

## Implementação

- `ResolucaoRoteamentoService` (domain) — avalia regras e devolve `(canal, templateId?)`.
- `CanalEnvioRouter` (infra) — mapeia canal→adapter; cada adapter implementa envio + normalização de webhook.
- ArchUnit: SDK/HTTP de provedor só em `infrastructure.channels` (reforça RULE-01/04).

## Casos de borda

- Duas regras com a mesma `prioridade` casando → desempate determinístico (ex.: `criado_em`); documentado e testado.
- Canal resolvido sem `config_canal` ativa → `422 comm.canal.nao-configurado`.
- Lead sem nenhum endereço para preferido nem fallbacks → `422 comm.roteamento.sem-canal`.
- Provedor trocado (ex.: TWILIO→SNS) na `config_canal` → próximo disparo usa o novo adapter sem mudança de código de domínio.

## Critérios de aceite (EARS)

- `WHEN routing is evaluated, THE SYSTEM SHALL apply active rules in ascending prioridade and select the first whose condicoes match the recipient context.`
- `WHERE the recipient lacks an address for the preferred channel, THE SYSTEM SHALL try the canais_fallback in order.`
- `IF no channel can be resolved for the recipient, THEN THE SYSTEM SHALL reject the dispatch with 422 error.code 'comm.roteamento.sem-canal'.`
- `WHEN the dispatch worker sends a message, THE SYSTEM SHALL select the adapter by (canal, config_canal.provedor) via CanalEnvioPort.`
- `IF the resolved canal has no active config_canal, THEN THE SYSTEM SHALL reject with 422 error.code 'comm.canal.nao-configurado'.`
- `THE SYSTEM SHALL keep the domain provider-agnostic — domain and application code SHALL depend only on Canal and CanalEnvioPort, never on a provider SDK.`
- `WHEN a new channel/provider is added, THE SYSTEM SHALL require only a new adapter and config_canal entry, with no change to routing or domain code.`
