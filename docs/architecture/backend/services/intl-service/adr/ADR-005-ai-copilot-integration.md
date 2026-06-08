# ADR-005 — AI Copilot via RAG Fundamentado + TechLab AI

**Status:** accepted

## Contexto

O AI Copilot é a capacidade-âncora de INTL: responder perguntas de negócio em linguagem natural.
O risco central é a **alucinação** (apresentar fato inventado como verdadeiro) e a violação da
regra do monorepo de **nunca chamar provedor de IA diretamente**. A operação é multi-tenant e
sensível a LGPD.

## Decisão

Implementar o Copilot como **RAG fundamentado**, sempre via **TechLab AI**:

1. **Recuperação primeiro:** `SearchPort.search()` recupera evidência (`knowledge-nodes` + *facts*
   relevantes) **filtrada por `empresa`**.
2. **Composição via TechLab AI:** a evidência *grounded* é passada às capabilities `knowledge`
   (embeddings/RAG) e `orchestration` (composição) — **nunca** o resultado bruto do Elastic a um
   provedor de IA direto. Versionamento de prompt/custo/auditoria ficam na TechLab AI.
3. **Resposta com citações:** toda resposta referencia ids de documentos recuperados. Resposta sem
   citação fundamentada é marcada **`nao_fundamentada`** (entregue, mas sinalizada).
4. **Read-only:** o Copilot do MVP **não** muta dados de outros módulos (sem ações/automações).
5. **Degradação graciosa:** circuit breaker + timeout na TechLab AI; em falha, **modo
   recuperação-apenas** (lista a evidência sem síntese, `status=DEGRADADA`). O serviço não cai.
6. **Síncrono:** a UX conversacional exige resposta imediata; protegido por Resilience4j.
7. **Auditoria/custo:** cada resposta persiste `modelo`/`custo_tokens`/`latencia_ms` e emite
   `journey-os.copilot.resposta.gerada` → `ai-copilot-events`.

## Alternativas consideradas

- **LLM puro sem RAG:** fluência sem fundamentação → alucinação; rejeitada (viola INV-2).
- **Chamada direta a provedor de IA (OpenAI/Anthropic/…):** viola a regra do monorepo (IA só via
  TechLab AI); rejeitada.
- **Copilot assíncrono (fila + callback):** UX inadequada para diálogo; rejeitada no MVP.
- **Copilot com ações (escrita de volta/agentes):** risco e escopo altos para o MVP; adiada.

## Consequências

**Positivas:** respostas auditáveis e citáveis; conformidade com a regra de IA do monorepo;
resiliência (degrada, não cai); controle de custo por `empresa`.
**Negativas:** qualidade depende da curadoria da Base de Conhecimento e da cobertura dos *facts*;
latência somada (recuperação + composição) — mitigada por timeouts/circuit breaker; resposta
degradada é menos útil (porém honesta).

## Referências

- `docs/architecture/integrations/elastic-stack-integration.md` §7 (fluxo RAG com TechLab AI)
- `docs/architecture/integrations/techlab-ai-integration.md` (contrato — placeholder até P3)
- CLAUDE.md — "Never call an AI provider directly — always via TechLab AI"
- [[ADR-003-event-platform-indexing-strategy]] · [[ADR-004-multitenant-strategy]]
