# COMM-010 -- Channel adapters (CanalEnvioPort) + CanalEnvioRouter

## Contexto
Abstração provedor-agnóstica de envio (ADR-005): um port único `CanalEnvioPort` com um adapter
por canal/provedor, selecionado em runtime.

## Spec de referencia
- SPEC-03-channel-routing
- SPEC-10-integrations

## Escopo
- `CanalEnvioPort` (application/port/out): `ResultadoEnvio enviar(Mensagem, ConfigCanal)`.
- Adapters em `infrastructure/channels`: `WhatsAppEnvioAdapter`, `EmailEnvioAdapter`, `TelegramEnvioAdapter`, `SmsEnvioAdapter` (HTTP + Resilience4j).
- `CanalEnvioRouter` (factory): seleciona adapter por `(canal, config_canal.provedor)`.
- Cada adapter normaliza callback do provedor → `EventoEntrega` canônico (consumido por COMM-014).
- ArchUnit: SDK/HTTP de provedor só em `infrastructure.channels`.

## Resultado esperado
Domínio envia por `canal` sem conhecer provedor; novo canal/provedor = novo adapter, sem mudar domínio.

## Criterios de aceite
- [ ] Cada canal seleciona o adapter correto por `(canal, provedor)`.
- [ ] Domínio/aplicação não importam SDK de provedor (ArchUnit).
- [ ] Adicionar canal = novo adapter + `config_canal`, sem tocar roteamento/domínio.

## Dependencias
- COMM-002 (precede)
- INT-COMM-004 (channel providers)

## Estimativa
L

## Prioridade
P4
