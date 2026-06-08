# ADR-002 — Fronteira de Serviço Único (Copilot + Plataforma)

**Status:** accepted

## Contexto

INTL reúne duas capacidades: (a) **AI Copilot + Base de Conhecimento** (domínio rico) e
(b) **governança da plataforma de dados Elastic + leitura analítica** (transversal). Caberia
dividir em dois serviços desde o início.

## Decisão

Implementar **um único serviço** `intl-service` (`com.journeyos.intl`, porta 8087) contendo as
duas capacidades, separadas por **fronteiras internas de portas** distintas:
`KnowledgePort`/`OrchestrationPort` (Copilot) vs `SearchPort` analítico + `IndexPort`/registro de
índices (Plataforma). Ambas compartilham o contexto de `empresa`, o `elastic-client-lib` e o ciclo
de autorização `intl.*`.

## Alternativas consideradas

- **Dois serviços desde o MVP (`intl-copilot` + `intl-platform`):** dobra a malha de rede,
  deploy e coordenação de `empresa`/autorização sem ganho no MVP; rejeitada.
- **Fundir a plataforma em WRKS/infra:** misturaria responsabilidades de identidade com dados;
  rejeitada.

## Consequências

**Positivas:** menor overhead operacional; reuso direto do `elastic-client-lib` e do
`EmpresaContextHolder`; um único pipeline de autorização.
**Negativas:** um serviço com dois "sabores" de carga (síncrono de IA vs leitura analítica) — exige
isolamento de pools/circuit breakers. A separação por portas mantém aberto o caminho de extrair um
`intl-platform-service` no pós-MVP sem reescrever o domínio.

## Referências

- `04-backend-architecture-direction.md` §2
- [[ADR-003-event-platform-indexing-strategy]]
