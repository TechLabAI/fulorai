# Event Contracts — intl-service (INTL)

> Event bus: **Kafka / AWS MSK**. Envelope canônico Journey OS (`eventId`, `tipo`, `empresa`,
> `ocorridoEm`, `correlationId`, `versao`, `payload`). Idempotência por `eventId` (consumidores)
> e por doc-id determinístico (projeções Elastic). EARS guide:
> `docs/architecture/backend/standards/ears-notation.md`.

## 1. Eventos publicados

### 1.1 `journey-os.copilot.resposta.gerada` (âncora)

Emitido após o copiloto gerar uma resposta (fundamentada, não-fundamentada ou degradada).
Projetado em `ai-copilot-events` (fact).

```json
{
  "eventId": "uuid",
  "tipo": "journey-os.copilot.resposta.gerada",
  "empresa": "slug",
  "ocorridoEm": "ISO-8601",
  "correlationId": "uuid",
  "versao": 1,
  "payload": {
    "conversaId": "uuid",
    "mensagemId": "uuid",
    "usuarioRef": "uuid",
    "status": "RESPONDIDA | NAO_FUNDAMENTADA | DEGRADADA",
    "qtdCitacoes": 3,
    "modelo": "string | null",
    "custoTokens": 1234,
    "latenciaMs": 850
  }
}
```

EARS:
- WHEN uma resposta do copiloto é persistida, THE SYSTEM SHALL publicar exatamente um `journey-os.copilot.resposta.gerada`.
- THE SYSTEM SHALL incluir `empresa` e `correlationId` no envelope de todo evento publicado.
- WHILE em modo degradado, THE SYSTEM SHALL publicar o evento com `modelo=null` e `custoTokens=0`.

*(Pós-MVP: `journey-os.insight.gerado`, `journey-os.no.conhecimento.indexado`.)*

## 2. Eventos consumidos

| Evento | Origem | Reação de INTL |
|---|---|---|
| `journey-os.asset.versao.publicada` | ASST | Ingere/atualiza nó de conhecimento a partir do conteúdo publicado (fonte `ASSET`). |
| `journey-os.empresa.provisionada` | WRKS | Seed: cria `base_conhecimento` da `empresa` + registro de índices por tenant (idempotente). |
| `journey-os.modelo.acesso.alterado` | WRKS | Invalida cache local de AccessDecision. |

EARS:
- WHEN `journey-os.empresa.provisionada` é consumido, THE SYSTEM SHALL criar a `base_conhecimento` da `empresa` de forma idempotente (no-op se já existir).
- WHEN `journey-os.asset.versao.publicada` é consumido, THE SYSTEM SHALL criar/atualizar um nó de conhecimento `fonte=ASSET` referenciando `assetId:versao` e agendá-lo para indexação.
- IF o mesmo `eventId` é reentregue, THEN THE SYSTEM SHALL tratá-lo como no-op (idempotência por `eventId`).
- IF o consumo falha de forma transitória, THEN THE SYSTEM SHALL repetir com backoff; após o limite, rotear para a DLQ de mensageria.

## 3. Idempotência

| Fluxo | Chave | Janela |
|---|---|---|
| Consumo Kafka | `eventId` | dedupe por `eventId` (consumer offset + verificação). |
| Projeção Elastic | doc-id determinístico (`evento_id` no ledger `evento_indexado`) | permanente (no-op em reprojeção). |
| Ingestão de asset | `assetId:versao` | atualiza nó existente em vez de duplicar. |

## 4. Versionamento de payload

- Campo `versao` no envelope; mudanças retrocompatíveis incrementam `versao` mantendo campos
  antigos. Consumidores ignoram campos desconhecidos (tolerant reader).
