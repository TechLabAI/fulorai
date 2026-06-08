# ADR-003 — Mensageria + IA: eventos async (Kafka) + composição sync resiliente (TechLab AI)

**Status:** accepted

## Contexto

ASST precisa (a) notificar outros módulos quando um asset é publicado/aprovado/rejeitado e
(b) compor conteúdo via TechLab AI no Asset Studio. São naturezas diferentes: notificação de
domínio (desacoplada) vs. orquestração de uma capacidade externa (com resposta esperada na UX).

## Decisão

- **Eventos de domínio → assíncronos via Kafka/AWS MSK** com padrão **outbox** + idempotência:
  `journey-os.asset.criado`, `journey-os.asset.aprovado`, `journey-os.asset.rejeitado`,
  `journey-os.asset.versao.publicada` (evento-âncora). Consumidores (COMM/JRNY/SALE) reagem sem
  acoplamento síncrono. ASST consome `journey-os.modelo.acesso.alterado` (invalida cache de
  AccessDecision) e `journey-os.empresa.provisionada` (seed de catálogo).
- **Asset Studio (TechLab AI `document_composition`) → síncrono com proteção Resilience4j**
  (timeout + circuit breaker + retry limitado) e **fallback graceful**: se a TechLab AI estiver
  indisponível, o endpoint do Studio retorna degradação explícita (ProblemDetail) sem afetar
  CRUD/versionamento/aprovação/publicação. Composições longas podem migrar para **assíncrono**
  (`202 Accepted` + callback/polling) pós-MVP.
- **Indexação Elastic → síncrona best-effort**, não bloqueia a publicação (projeção reconciliável).

## Alternativas consideradas

- **Composição IA também assíncrona desde o MVP:** melhor para picos, mas complica a UX (precisa de polling/notificação) sem necessidade no volume inicial. Adiada (pós-MVP).
- **Eventos síncronos (Feign) para notificar consumidores:** acoplaria ASST aos consumidores e propagaria falhas. Rejeitada — leitura de assets publicados é via Feign `AssetQueryClient`, mas a *notificação* é via evento.

## Consequências

**Positivas:** publicação desacoplada e auditável; Studio resiliente; falha de IA não derruba o hub.

**Negativas:** complexidade de outbox/idempotência; composição síncrona limita o tamanho/tempo da geração no MVP (mitigado por timeout e plano async pós-MVP).

## Referências

- `docs/architecture/backend/standards/platform-patterns.md` (Kafka, outbox, Feign+Resilience4j)
- `docs/architecture/integrations/techlab-ai-integration.md` (`document_composition`)
- ADR global: `docs/architecture/backend/adr/ADR-003-multi-tenancy.md` (contexto de plataforma)
