# INT-COMM-004 -- Channel providers (adapters + webhook normalization)

## Contexto
Integração com provedores externos de canal (Meta WABA, SES/SendGrid, Telegram Bot, Twilio/SNS)
através dos adapters sob `CanalEnvioPort` (ADR-005).

## Spec de referencia
- integration-contracts.md §1
- SPEC-03-channel-routing
- SPEC-10-integrations

## Escopo
- Adapters HTTP por canal/provedor (envio) com Resilience4j (timeout/CB/retry/backoff 1s/5s/30s).
- Normalização de webhook por provedor → `EventoEntrega` canônico (assinatura verificada).
- Credenciais resolvidas de `config_canal.credencial_ref` (secret manager); nunca hardcoded/logado.
- Rate-limit (429) → backoff no worker; falha após retries → FALHADA + DLQ.

## Resultado esperado
Envio multicanal real via adapters; callbacks normalizados atualizam o ciclo de vida.

## Criterios de aceite
- [ ] Cada provedor envia via seu adapter sob Resilience4j (testado com WireMock/sandbox).
- [ ] Webhook com assinatura válida → `EventoEntrega`; inválida → 401.
- [ ] Provedor fora após retries → FALHADA + DLQ.

## Dependencias
- COMM-010 (precede)
- COMM-011 (config de canal)

## Estimativa
L

## Prioridade
P4
