# ADR-002 — IA orquestrada via serviço dedicado TechLab AI (não chamada direta a provider)

> **Data:** 2026-06-04
> **Status:** draft (BA)
> **Decisor:** Arquiteto (Danilo Amaral) — pendente de promoção

---

## Contexto

A IA é diferencial central do Journey OS: AI Copilot com RAG sobre contexto
operacional (lead, jornada, asset, receita), recomendação de assets/ofertas e
explicabilidade — sempre com **evidência citada** e **fallback** quando faltam
dados (Framing §2.4/§9; LBC §8). A IA opera como camada transversal, não como
chatbot isolado.

Duas decisões acopladas: **(1) onde mora a orquestração de IA** (embutida nos
serviços de domínio Java vs serviço dedicado) e **(2) lock-in em um provider de
LLM vs abstração agnóstica**. O backend de domínio é Java (ADR-001), mas
bibliotecas maduras de orquestração de IA (RAG, prompt/policy, instructor,
clients oficiais) vivem em Python. Já existe o serviço `techlab-ai`
(Python/FastAPI) no ecossistema do framework, pensado como camada de
orquestração. Constraint TECH-005 impõe IA via TechLab AI, não chamada direta a
provider.

---

## Opções consideradas

### Opção A — Serviço dedicado TechLab AI (orquestração + abstração de provider)
- **Vantagens:**
  - Cumpre TECH-005; provider de LLM trocável sem refatorar domínio.
  - RAG híbrido (pgVector + Elastic, filtrado por `workspace_id`), guardrails,
    fallback e log de custo/latência centralizados num só lugar — coerente com o
    princípio de evidência (Framing §9.3) e com o modelo de receita que pode
    cobrar por consumo de IA em V2 (LBC §9).
  - Stack Python idiomática para IA sem contaminar o backend Java.
  - `techlab-ai` já existe — reduz custo de implementação.
- **Desvantagens:**
  - Hop HTTP adiciona latência (~50-200ms).
  - Componente extra a operar (deploy, monitoramento) — peso para time enxuto.
- **Custo:** baixo — serviço já existe no framework.

### Opção B — Chamada direta a provider LLM (ex.: OpenAI, como no PRD §10)
- **Vantagens:**
  - Latência menor (sem hop intermediário).
  - Simplicidade aparente no curto prazo.
- **Desvantagens:**
  - Lock-in ao provider; trocar provider = refator em todo serviço que chama IA.
  - RAG/guardrails/fallback/custo duplicados e dispersos — risco de Copilot
    alucinar (risco do LBC §12) por falta de camada de evidência consistente.
  - Viola TECH-005.
- **Custo:** baixo inicial, alto para evoluir e governar.

### Opção C — Biblioteca de IA embarcada no backend Java
- **Vantagens:**
  - Sem hop HTTP (mesma JVM).
- **Desvantagens:**
  - Bibliotecas Java de IA/RAG imaturas frente a Python.
  - Ainda lock-in implícito ao client embarcado; atualização = release
    coordenado de todos os serviços.
- **Custo:** médio inicial, alto de manutenção.

---

## Decisão

Escolhida: **Opção A — serviço dedicado TechLab AI**.

---

## Justificativa

1. **Cumpre TECH-005 nativamente e protege o diferencial.** O Copilot do
   Journey OS só tem valor se responder com evidência e fallback consistentes
   (LBC §8.4, risco de alucinação no §12). Concentrar RAG, guardrails e citação
   de fonte na TechLab AI garante esse comportamento em todos os pontos de IA
   (advisors, chat, recomendação) sem reimplementação por domínio.

2. **Rastreabilidade de custo de IA por workspace.** Multi-tenant + possível
   precificação por uso de IA (LBC §9) exige tagear cada chamada por
   (workspace, feature). Distribuído seria pesadelo operacional; centralizado é
   trivial.

3. **Stack certa para cada problema.** Python para orquestração de IA, Java para
   domínio (ADR-001). A arquitetura multi-runtime já é assumida.

O domínio Java nunca chama provider direto: chama a TechLab AI via port/adapter
(ADR-004), e a TechLab AI decide qual LLM usar internamente.

---

## Trade-offs aceitos

- **Perdemos:** latência mais baixa de chamada direta. Justificativa: o Copilot
  do Journey OS responde em painel/chat (a tela mostra estado "recuperando
  evidência..."), não em loop transacional crítico; ~100-200ms é aceitável.
- **Perdemos:** simplicidade de um componente a menos. Justificativa: a
  complexidade fica encapsulada e o ROI de portabilidade/governança compensa.
- **Perdemos:** o provider OpenAI fixo do PRD §10. Justificativa: lock-in é
  risco estratégico; abstração via TechLab AI é mais segura.

---

## Como reverter se a decisão se mostrar errada

Caminho de reversão (improvável):
1. Mover orquestração para biblioteca embarcada no backend Java.
2. Refatorar os adapters de IA (`AiCopilotOrchestrator` e ports) dos domínios.
3. Reimplementar RAG/guardrails/métricas em Java.

**Custo estimado:** 2-4 meses de 1-2 devs. A reversão **não destrói** o que foi
feito — a TechLab AI pode coexistir como serviço opcional durante a transição.

---

## Sinais que indicariam que está errada

- Latência do hop impactando UX percebida do Copilot (p95 > 5s nas respostas
  típicas com evidência) de forma consistente.
- Custo de operar o serviço extra dominando o tempo do time enxuto (>20%).
- Surgir biblioteca Java de RAG/orquestração madura o suficiente para
  substituir o ecossistema Python.

---

## Consequências

- **Em código:** domínios consomem `techlab-ai` via HTTP REST por ports/adapters
  (`AiCopilotOrchestrator`, Framing §6.11); contratos `/v1/*` versionados.
- **Em dados:** RAG híbrido pgVector (ADR-006) + Elastic (ADR-007), sempre
  filtrado por `workspace_id`; logs em `ai-copilot-events-*`.
- **Em deploy/monitoramento:** `techlab-ai` é serviço próprio; métricas de
  latência/erro de IA na observabilidade (OPS-001).

---

## Referências

- LBC §8 (como a IA gera valor), §9 (receita pode cobrar por uso de IA), §12 (risco de alucinação)
- Framing §2.4 (IA com evidência), §9 (estratégia de IA), §6.11 (AiCopilotOrchestrator)
- Constraints: TECH-005, REG-001 (PII em retrieval), OPS-001
- ADRs relacionados: ADR-001 (backend Java), ADR-003 (multi-tenancy / filtro por workspace),
  ADR-004 (IA via port/adapter), ADR-006/007 (fontes do RAG híbrido)
