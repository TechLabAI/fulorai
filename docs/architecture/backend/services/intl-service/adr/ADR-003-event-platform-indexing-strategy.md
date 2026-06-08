# ADR-003 — Plataforma de Dados: Indexação Descentralizada + Contrato Governado

**Status:** accepted

## Contexto

O Journey OS indexa *facts* em vários índices Elastic (`journey-events`, `routing-decisions`,
`communication-events`, `revenue-events`, `campaign-events`) além dos índices próprios de INTL
(`ai-copilot-events` *fact*, `knowledge-nodes` *dimension*) e dos índices de observabilidade
(`app-logs`, `traces`, `metrics`, `integration-logs`). A pergunta central: **quem escreve cada
índice** e **quem governa o contrato**? Os módulos JRNY/COMM/SALE já declaram (nos seus catálogos)
que projetam **os seus próprios** *facts* via o `elastic-client-lib`.

## Decisão

**Indexação descentralizada na escrita, centralizada no contrato:**

1. **Cada módulo produtor escreve os seus próprios *facts*** (JRNY → `journey-events`/`routing-decisions`,
   COMM → `communication-events`, SALE → `revenue-events`/`campaign-events`) usando o
   `elastic-client-lib`. INTL **não** reindexа *facts* alheios.
2. **INTL é o dono do contrato de dados da plataforma:** o **bloco de rastreabilidade de 8 campos**
   (D-269), o roteamento para **DLQ** (`journey-os_dlq`), o **registro de índices** + mapeamentos +
   políticas **ILM** (classes *dimension*/*fact* — D-272), e as convenções de bulk/idempotência.
3. **INTL escreve apenas os índices próprios:** `ai-copilot-events` e `knowledge-nodes`.
4. **INTL provê a leitura analítica cross-index** (`/api/v1/analytics/**`), agregando *facts* já
   projetados, sempre filtrando por `empresa` — read-only.
5. **Observabilidade** (`app-logs`/`traces`/`metrics`/`integration-logs`): INTL **declara** os
   índices/ILM; a **ingestão** é de agentes de infra/APM (Filebeat/OTel), não de código de domínio
   no MVP.

Idempotência por **doc-id determinístico**; toda indexação carrega o bloco de rastreabilidade +
`empresa`; violações → DLQ.

## Alternativas consideradas

- **INTL como único indexador (centralizado):** INTL consumiria todos os `journey-os.*` e escreveria
  todos os *facts*. Rejeitada — contradiz o ownership já arquitetado dos módulos, cria pipeline
  duplicado, ponto único de falha e acoplamento temporal (INTL teria de conhecer o schema de todos).
- **Sem governança central (cada um inventa seu contrato):** rejeitada — quebra a rastreabilidade
  (D-269) e a auditabilidade, e inviabiliza leitura analítica consistente.

## Consequências

**Positivas:** sem escrita dupla; cada módulo dono do seu dado; contrato único garante
rastreabilidade/DLQ/ILM consistentes; INTL foca em inteligência + leitura. Caminho aberto para
o Integration Hub e a ingestão de observabilidade no pós-MVP.
**Negativas:** o contrato vira dependência transversal (mudança no bloco de rastreabilidade afeta
todos os produtores) — versionar o contrato e validá-lo no `elastic-client-lib`/CI. A leitura
analítica depende de os produtores terem indexado corretamente.

## Referências

- `docs/architecture/integrations/elastic-data-contract.md` (D-269)
- `docs/architecture/integrations/elastic-stack-integration.md` (D-272, classes dimension/fact)
- `backend/services/elastic-client-lib/`
- [[ADR-004-multitenant-strategy]] · [[ADR-005-ai-copilot-integration]]
