# ADR-005 — Channel adapter pattern: `CanalEnvioPort` + adapters por canal (provedor-agnóstico)

**Status:** accepted

## Contexto

COMM precisa enviar por WhatsApp, e-mail, Telegram e SMS — cada um com um (ou mais) provedor
externo (Meta WABA, SES/SendGrid, Telegram Bot API, Twilio/SNS), com APIs, autenticação, formatos
de payload e formatos de callback (webhook) **totalmente diferentes**. Se o domínio/aplicação
conhecer cada provedor, (a) viola o hexagonal, (b) torna impossível testar roteamento/entrega sem
rede, e (c) faz cada novo canal/provedor reverberar pelo código todo. Ao mesmo tempo, o domínio
precisa raciocinar de forma uniforme sobre "enviar uma mensagem por um canal" e sobre o ciclo de
vida de entrega.

## Decisão

1. **Port único de saída `CanalEnvioPort`** (em `application/port/out`):
   ```
   ResultadoEnvio enviar(Mensagem mensagem, ConfigCanal config);
   ```
   O domínio/aplicação opera sobre o enum `Canal` e o `ConfigCanal` (provedor + identidade +
   `credencial_ref`) — **nunca** sobre um SDK de provedor.

2. **Um adapter por canal** em `infrastructure/channels`, implementando o port:
   `WhatsAppEnvioAdapter`, `EmailEnvioAdapter`, `TelegramEnvioAdapter`, `SmsEnvioAdapter`. Cada
   adapter (a) traduz a `Mensagem` para o payload do provedor, (b) chama o provedor via HTTP sob
   **Resilience4j** (timeout/CB/retry), (c) mapeia a resposta para `ResultadoEnvio`, e (d)
   **normaliza o callback** (webhook) do seu provedor para o `EventoEntrega` canônico
   (`ENVIADA`/`ENTREGUE`/`LIDA`/`FALHADA`/`REJEITADA`).

3. **Seleção em runtime** por um `CanalEnvioRouter` (factory): dado o `canal` da mensagem e o
   `config_canal.provedor` da empresa, resolve o adapter correto. Adicionar um canal/provedor =
   **novo adapter + entrada de config**, sem tocar domínio, roteamento ou casos de uso.

4. **Segredo do provedor** vem de `config_canal.credencial_ref` (secret manager / `${VAR}`),
   resolvido no adapter; **nunca** persistido em claro nem logado.

ArchUnit barra import de SDK/HTTP de provedor fora de `infrastructure.channels` (reforça RULE-01/04).

## Alternativas consideradas

- **Chamada direta ao provedor nos `@Service` de aplicação:** rápido de escrever, mas acopla o domínio a Meta/Twilio/SES, impede teste sem rede e quebra o hexagonal. Rejeitada.
- **Um microserviço por canal:** isolaria provedores, mas distribui cedo demais e duplica roteamento/idempotência (ver `ADR-002`). Rejeitada — canal é adapter, não serviço.
- **Biblioteca multicanal de terceiros (ex.: um "notification gateway" único):** reduz código, mas amarra o produto a um vendor e ao seu modelo de canais/preços; perde controle sobre fallback e normalização. Rejeitada no MVP (reavaliar pós-MVP).

## Consequências

**Positivas:** domínio provedor-agnóstico e testável; novo canal/provedor é aditivo (Open/Closed); normalização de callbacks num único ponto por canal; troca de provedor (ex.: Twilio→SNS) sem tocar o resto.

**Negativas:** cada adapter precisa mapear envio **e** webhook do seu provedor (trabalho por integração); a interface canônica (`CanalEnvioPort`/`EventoEntrega`) precisa ser estável o bastante para cobrir as diferenças entre canais (mitigado por `provedor_payload` jsonb preservando o bruto).

## Referências

- `02-architecture-blueprint.md` (§4 Internal Boundaries — `infrastructure/channels`)
- `03-initial-domain-framing.md` (§2 Aggregates — `ConfigCanal`, `Canal`; §5 Invariants)
- `04-backend-architecture-direction.md` (§5 External Integrations)
- `adr/ADR-003-messaging-strategy.md` (o worker de disparo invoca o adapter resiliente)
- `docs/architecture/backend/standards/platform-patterns.md` (Feign+Resilience4j)
