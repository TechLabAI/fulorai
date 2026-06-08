# ADR-001 — Arquitetura Hexagonal (Ports & Adapters)

**Status:** accepted

## Contexto

INTL integra múltiplas tecnologias voláteis e externas (TechLab AI, Elasticsearch, Kafka, JPA) e
precisa manter o domínio (Copilot/Conhecimento) puro e testável, alinhado ao padrão obrigatório do
monorepo Journey OS (RULE-01..09, ArchUnit).

## Decisão

Adotar arquitetura **hexagonal** com o pacote base `com.journeyos.intl` e as camadas
`api` / `application` / `domain` / `infrastructure`. O domínio não importa Spring nem JPA;
TechLab AI, Elasticsearch, Kafka e persistência ficam atrás de **portas** (`KnowledgePort`,
`OrchestrationPort`, `SearchPort`, `IndexPort`, `IntlEventPublisherPort`, repositórios).
`@Transactional` apenas em `application.service`. ArchUnit (`architectureCheck`) bloqueante.

## Alternativas consideradas

- **Camadas técnicas tradicionais (controller/service/repository sem portas):** acoplaria o
  domínio ao Elastic/TechLab AI; rejeitada (viola o padrão do monorepo, dificulta o fallback).
- **Arquitetura orientada a serviços internos sem domínio rico:** insuficiente para as invariantes
  de fundamentação/rastreabilidade.

## Consequências

**Positivas:** isolamento do domínio; troca de adapter (ex.: provedor de embedding) sem tocar o
núcleo; testabilidade; conformidade ArchUnit.
**Negativas:** mais interfaces/boilerplate; curva para mapear portas in/out.

## Referências

- `docs/architecture/backend/standards/hexagonal-patterns.md`
- CLAUDE.md — RULE-01..09
