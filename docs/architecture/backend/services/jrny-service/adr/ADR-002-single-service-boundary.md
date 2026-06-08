# ADR-002 — Fronteira: single service (builder + routing engine + decision log coesos)

**Status:** accepted

## Contexto

JRNY cobre o desenho de jornadas (Journey Builder), a decisão de roteamento (Routing Engine) e
o registro auditável dessas decisões (decision log). Poderíamos decompor (ex.: um serviço de
"builder" separado do "engine"), mas isso introduz coordenação distribuída cedo demais e quebra
a coesão entre a definição da jornada e a execução do roteamento que depende dela.

## Decisão

Implementar JRNY como **um único serviço** (`jrny-service`, `com.journeyos.jrny`), default do
monorepo. O Routing Engine é um **componente de domínio interno** (avalia regras + orquestra o
assist de IA via port `out`), não um serviço separado. A coesão entre `Jornada`/`Estagio`/
`RegraRoteamento` (definição) e `InscricaoJornada`/`DecisaoRoteamento` (execução) favorece a
transação local e a consistência forte das transições de inscrição.

## Alternativas consideradas

- **Routing Engine como serviço separado:** isolaria a carga de avaliação/IA, mas exigiria sincronização entre a definição da jornada e o motor; complexidade distribuída sem ganho no MVP. Rejeitada (reavaliar se a carga de roteamento justificar escala independente).
- **Decision log como serviço/Event Platform separado:** a auditoria já é projetada para Elastic e consumível por INTL; um serviço dedicado só adicionaria salto de rede no caminho crítico da decisão. Rejeitada (INTL consome os eventos/índices, não substitui o log local).

## Consequências

**Positivas:** transações locais para inscrição/decisão; deploy/observabilidade simples; menos contratos internos.

**Negativas:** a carga de roteamento (e o assist de IA) compartilha o mesmo processo do CRUD de jornada — mitigado por circuit breaker/timeout no assist e, se necessário, por escala horizontal do serviço pós-MVP.

## Referências

- `04-backend-architecture-direction.md` (§2 Service Boundary)
- ADR global: `docs/architecture/backend/adr/ADR-002-modular-monolith.md`
