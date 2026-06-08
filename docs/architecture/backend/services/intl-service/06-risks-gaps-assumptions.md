# 06 — Risks, Gaps & Assumptions — INTL

## 1. Riscos

| # | Risco | Impacto | Mitigação |
|---|---|---|---|
| R-1 | **Dependência da TechLab AI** (síncrona no caminho do Copilot) | Indisponibilidade degrada a UX | Circuit breaker + timeout curto + **fallback recuperação-apenas**; resposta marcada `DEGRADADA`. |
| R-2 | **Alucinação / resposta não fundamentada** | Perda de confiança, decisão errada | RAG obrigatório + **citações verificáveis**; resposta sem citação marcada `nao_fundamentada`; nunca apresentar fato alucinado como confirmado (INV-2). |
| R-3 | **Vazamento cross-tenant na recuperação** | Violação LGPD/grave | Filtro `empresa` obrigatório em **toda** query Elastic; PG por schema; testes de isolamento. |
| R-4 | **`openapi.json` da TechLab AI vazio** (P3 bloqueado) | DTOs/endpoints exatos pendentes | Programar contra a capability (`knowledge`/`orchestration`) via porta; gerar DTOs no sync (P3). |
| R-5 | **Ambiguidade de ownership de índice** (quem escreve os *facts*) | Escrita dupla/conflito | ADR-003: **descentralizado** — produtores escrevem seus *facts*; INTL só governa + lê + escreve os próprios. |
| R-6 | **Custo da IA** (tokens) sem controle | Estouro de orçamento | Registrar `custo_tokens`/`modelo` por mensagem; métricas e limites por `empresa` (pós-MVP: quota). |
| R-7 | **Volume/ILM dos *facts*** mal dimensionado | Custo/latência Elastic | Classes dimension/fact (D-272); ILM rollover; `registro_indice` governa. |
| R-8 | **Embedding drift** (mudança de modelo) | Recuperação inconsistente | Versão de embedding por nó; reembedding controlado; `knowledge-nodes` reindexável. |

## 2. Gaps Conhecidos

- **Contrato TechLab AI** (`knowledge`/`orchestration`) não materializado — `integrations/techlab-ai/openapi.json`
  vazio (P3 pendente). Endpoints/DTOs exatos definidos no sync.
- **Gramática da analítica** (quais agregações cross-index o MVP expõe) a fechar em specs.
- **Decisão `registro_indice` global vs configuração** a confirmar no data-model.
- **Gradle toolchain ausente no ambiente** → gates de compile/ArchUnit/BDD deferidos (ver
  `[[gradle-toolchain-absent]]`).

## 3. Suposições a Validar

- A TechLab AI expõe `knowledge` (embeddings + RAG) e `orchestration` (composição) consumíveis por HTTP.
- pgVector já habilitado pela V1 global (extensão `vector`).
- O `elastic-client-lib` cobre `SearchPort`/`IndexPort` + DLQ + validação do bloco de rastreabilidade.
- Os módulos produtores (JRNY/COMM/SALE) já indexam seus *facts* conforme o contrato governado por INTL.
- ASST expõe `AssetQueryClient` para leitura do conteúdo publicado (fonte de conhecimento).

## 4. Dependências Críticas

| Dependência | Tipo | Bloqueia |
|---|---|---|
| **WRKS** (AccessDecision/JWT, eventos tenant) | Feign + Kafka | Autorização e seed por tenant. |
| **TechLab AI** (`knowledge`/`orchestration`) | HTTP | Composição fundamentada (com fallback). |
| **Elasticsearch** + `elastic-client-lib` | lib/HTTP | Recuperação RAG, analítica e projeções. |
| **MIG** | pré-condição | Schema `emp_<slug>` + (opcional) `registro_indice` global. |
| **ASST** (`AssetQueryClient` + evento) | Feign + Kafka | Ingestão de conhecimento a partir de asset. |
| **Sync TechLab AI (P3)** | processo | DTOs/endpoints exatos. |
