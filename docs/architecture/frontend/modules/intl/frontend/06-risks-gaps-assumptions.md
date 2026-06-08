# 06 — Risks, Gaps, Assumptions — INTL · Frontend

## 1. Riscos

| # | Risco | Categoria | Mitigação |
|---|---|---|---|
| R1 | **Latência alta/variável do Copilot** (RAG + composição de IA) degrada a percepção de UX. | UX/perf | Estado `pensando` imediato (< 100 ms), cancelamento via `AbortController`, timeout amigável; observability de p95 pergunta→resposta. |
| R2 | **Render de resposta degradada como se fosse fato** — pior falha possível do módulo (quebra a confiança). | UX/correção | INV-FE-1: tratamento visual dirigido por `status` do BE; `NAO_FUNDAMENTADA`/`DEGRADADA` nunca renderizam citações; testes Playwright cobrindo os 3 status. |
| R3 | **Citação não resolve ao documento-fonte** (deep-link quebrado entre `indice`/`documentoId` e a UI do módulo dono). | Integração | MVP: citação abre painel lateral com `trecho` + metadados (sem exigir navegação cross-módulo); deep-link real é incremento posterior. |
| R4 | **Vazamento cross-empresa** na troca de empresa (conversa/listas da empresa anterior). | Segurança/UX | Efeito de reset no `EmpresaContextService`: cancela in-flight + limpa conversa + recarrega; e2e de isolamento. |
| R5 | **Volume de mensagens/nós** em conversas longas / bases grandes degrada a lista. | Perf | Paginação no Knowledge (`page/size`); virtualização da lista de mensagens se necessário (medir antes). |
| R6 | **Contrato BE instável** (`status` extra, shape de citação) quebra o render. | Contrato | DTOs derivados do `api-contract.md`; `backend-api-cross-link.md` versiona o acoplamento; guard de status desconhecido → trata como degradada. |
| R7 | **Bundle size** do módulo (chat + dashboards). | Perf | Lazy por feature (`loadComponent`); gráficos de Analytics carregados sob demanda. |

## 2. Gaps Conhecidos

- **Endpoints exatos da TechLab AI** ainda pendentes do sync upstream (P3 — `openapi.json` vazio).
  Não afeta o FE diretamente (o FE fala só com `intl-service`), mas o shape final de `citacoes`
  pode evoluir.
- **Deep-link de citação → documento dono** (LEAD/JRNY/SALE) depende das telas desses módulos
  existirem — fora do MVP de INTL; tratado como painel lateral local por ora.
- **Streaming (SSE)** não tem endpoint no BE — feature-flag `intl.copilot-streaming` reservada
  (ADR-005).

## 3. Suposições a Validar

- A latência típica de uma pergunta do Copilot cabe num estado `pensando` aceitável (validar p95
  real contra o success-signal).
- O volume de nós por empresa no MVP é compatível com tabela paginada simples (sem busca avançada).
- pt-BR é suficiente no MVP (sem i18n multi-idioma).
- Devices alvo são desktop-first (operação de growth) — responsivo, mas não mobile-first.

## 4. Dependências Críticas

- **BE `intl-service`** endpoints `/api/v1/{copilot,knowledge,analytics}` (api-contract.md).
- **Access Layer (WRKS)** — `auth-session`, `empresa-context`, `access-decision` operacionais
  (WRKS FE já scaffoldado/registrado no Shell).
- **`@journeyos/shared/*`** — `ui-tokens`, `ui-feedback`, `ui-components`, `error-model`,
  `access-http-base`, `observability` (Wave-0 concluída).
- **Shell** (`journey-os-web`) — registro do `INTL_MODULE_DESCRIPTOR` via `module-descriptors.ts`.

---

## Referências

- `01-architectural-vision.md` (success signals) · `05-state-and-data-flow.md` (error handling)
- BE: `docs/architecture/backend/services/intl-service/06-risks-gaps-assumptions.md`
