# SPEC-03 — View Models — INTL

> View-models por tela como `type` TypeScript, expondo `Signal<T>` (leitura) + eventos de UI
> (callbacks emitidos pela page). Derivações via `computed()`. Sem NgRx.

## feature-copilot

```typescript
type CitacaoVM = {
  documentoId: string;
  indice: string;
  trecho: string;
  score: number;
};

type MensagemVM = {
  id: string;
  papel: 'USUARIO' | 'COPILOTO';
  conteudo: string;
  status?: 'PENDENTE' | 'RESPONDIDA' | 'NAO_FUNDAMENTADA' | 'DEGRADADA' | 'ERRO';
  citacoes: CitacaoVM[];
  modelo?: string;
  custoTokens?: number;
  latenciaMs?: number;
  criadaEm: string;
};

type ConversaListItemVM = {
  id: string;
  titulo: string;
  estado: 'ABERTA' | 'PROCESSANDO' | 'RESPONDIDA' | 'ERRO';
  atualizadaEm: string;
};

type CopilotVM = {
  conversas: Signal<ConversaListItemVM[]>;
  conversaAtual: Signal<string | null>;
  messages: Signal<MensagemVM[]>;
  status: Signal<'idle' | 'pensando' | 'respondida' | 'degradada' | 'erro'>;
  podeEnviar: Signal<boolean>;          // computed: !temPendente() && textoValido()
  loading: Signal<boolean>;
  error: Signal<AppError | null>;
};
// Eventos UI: novaConversa(titulo?), selecionarConversa(id), enviarPergunta(texto, topK?),
//             cancelarPergunta(), abrirCitacao(c: CitacaoVM)
```

## feature-knowledge

```typescript
type NoConhecimentoRowVM = {
  id: string;
  titulo: string;
  tags: string[];
  fonte: 'MANUAL' | 'ASSET';
  status: 'RASCUNHO' | 'INDEXADO' | 'ARQUIVADO';
  versao: number;
  atualizadoEm: string;
};

type KnowledgeFiltrosVM = { q: string; tag: string | null; status: string | null; page: number; size: number };

type KnowledgeListVM = {
  page: Signal<{ items: NoConhecimentoRowVM[]; total: number; page: number; size: number }>;
  filtros: Signal<KnowledgeFiltrosVM>;
  loading: Signal<boolean>;
  error: Signal<AppError | null>;
  canWrite: Signal<boolean>;            // computed via AccessDecisionService
};
// Eventos UI: buscar(filtros), abrirNovo(), abrirNo(id), indexar(id), arquivar(id)

type NoConhecimentoFormVM = {
  no: Signal<{ id?: string; titulo: string; conteudo: string; tags: string[]; fonte: { tipo: 'MANUAL'; referencia?: string } } | null>;
  saving: Signal<boolean>;
  indexState: Signal<'idle' | 'indexando' | 'indexado' | 'retry'>;  // 'retry' = 503 embedding-unavailable
  error: Signal<AppError | null>;
};
// Eventos UI: salvar(form), indexar(), voltar()
```

## feature-analytics

```typescript
type FunilVM = { periodo: string; etapas: { nome: string; total: number }[] };
type CopilotUsageVM = { totalRespostas: number; custoTokens: number; taxaFundamentadas: number; taxaDegradadas: number };

type AnalyticsVM = {
  funil: Signal<FunilVM | null>;
  copilotUsage: Signal<CopilotUsageVM | null>;
  periodo: Signal<string>;
  granularidade: Signal<string>;
  loading: Signal<boolean>;
  error: Signal<AppError | null>;
};
// Eventos UI: mudarPeriodo(p), mudarGranularidade(g)
```

## Notas

- Todos os VMs são derivados de respostas escopadas por `empresa`; um `effect()` na facade reage à
  troca de empresa (`EmpresaContextService`) limpando conversa/listas/dashboards.
- `AppError` vem de `@journeyos/shared/error-model`.
- `podeEnviar` e `canWrite` são `computed()` — nunca lógica de RBAC inline no template.

## Critérios de aceite (EARS)

- `THE SYSTEM SHALL derive every INTL view-model from empresa-scoped BE responses and SHALL NOT expose raw BE entities to components.`
- `WHEN the active empresa changes, THE SYSTEM SHALL clear conversations, lists and dashboards before loading the new empresa data.`
- `THE SYSTEM SHALL compute podeEnviar as true only WHILE there is no pending message and the question text is valid.`
- `THE SYSTEM SHALL compute canWrite via AccessDecisionService and SHALL NOT embed RBAC logic in templates.`
- `WHEN a copilot answer arrives, THE SYSTEM SHALL render citations only in the final answer status and never in PENDENTE.`
