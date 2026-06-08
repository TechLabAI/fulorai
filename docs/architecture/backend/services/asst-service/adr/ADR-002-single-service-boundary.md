# ADR-002 — Fronteira: single service (asset + studio + busca coesos)

**Status:** accepted

## Contexto

ASST cobre catálogo de assets, versionamento, workflow de aprovação, Asset Studio (composição
via IA) e Asset Intelligence/busca (Elastic). Poderíamos decompor (ex.: um serviço de "studio"
separado do "catálogo"), mas isso introduz coordenação distribuída cedo demais.

## Decisão

Implementar ASST como **um único serviço** (`asst-service`, `com.journeyos.asst`), default do
monorepo. O Asset Studio e o Asset Intelligence são **casos de uso internos** (orquestram
TechLab AI e Elastic via ports `out`), não serviços separados. A coesão do agregado `Asset`
(que controla versões e aprovações) favorece a transação local e a consistência forte das
transições de estado.

## Alternativas consideradas

- **Studio como serviço separado:** isolaria a carga de IA, mas exigiria sincronização entre "rascunho composto" e "asset"; complexidade distribuída sem ganho no MVP. Rejeitada (reavaliar se a carga de composição justificar escala independente).
- **Busca como serviço separado:** Elastic já é externo; um serviço dedicado só adicionaria salto de rede. Rejeitada.

## Consequências

**Positivas:** transações locais para a state machine; deploy/observabilidade simples; menos contratos internos.

**Negativas:** a carga de IA (Asset Studio) compartilha o mesmo processo do CRUD — mitigado por circuit breaker/timeout e, se necessário, por composição assíncrona pós-MVP (ver ADR-003).

## Referências

- `04-backend-architecture-direction.md` (§2 Service Boundary)
- ADR global: `docs/architecture/backend/adr/ADR-002-modular-monolith.md`
