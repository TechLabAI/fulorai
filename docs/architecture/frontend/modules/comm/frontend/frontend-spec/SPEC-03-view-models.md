# SPEC-03 — View Models — COMM · Frontend

> View-models por tela como signals expostos pelas facades. Eventos UI = callbacks emitidos pelas pages.
> Tipos base: ver `03-domain-framing-frontend.md`.

## Tipos de domínio (FE)

```typescript
type Canal = 'WHATSAPP' | 'EMAIL' | 'TELEGRAM' | 'SMS';
type TipoTemplate = 'TRANSACIONAL' | 'MARKETING' | 'NOTIFICACAO';
type EstadoTemplate = 'RASCUNHO' | 'ATIVO' | 'ARQUIVADO';
type EstadoEntrega = 'PENDENTE' | 'ENFILEIRADA' | 'ENVIADA' | 'ENTREGUE' | 'LIDA' | 'FALHADA';
type StudioState = 'idle' | 'composing' | 'draft-pronto' | 'degradado';
```

## Catálogo de templates — `TemplateCatalogVM`

```typescript
type TemplateCatalogVM = {
  items: Signal<TemplateResumoVM[]>;
  loading: Signal<boolean>;
  error: Signal<AppError | null>;
  filtro: Signal<{ canal?: Canal; tipo?: TipoTemplate; estado?: EstadoTemplate; q?: string }>;
  page: Signal<{ index: number; size: number; total: number }>;
};
// eventos UI: onFilterChange(f), onOpen(id), onNovo(), onPage(index)
```

## Editor de template — `TemplateEditorVM`

```typescript
type TemplateEditorVM = {
  template: Signal<TemplateVM | null>;
  loading: Signal<boolean>;
  error: Signal<AppError | null>;
  acoesDisponiveis: Signal<TemplateAcao[]>;        // computed por estado + permissão
  variaveisInvalidas: Signal<string[]>;             // computed: placeholders usadas não declaradas (UINV-1)
  assuntoObrigatorio: Signal<boolean>;              // computed: canal === 'EMAIL' (UINV-2)
};
// eventos UI: onSave(patch), onActivate(), onArchive(), onInsertPlaceholder(nome), onAbrirStudio()
```

## Template Studio — `TemplateStudioVM`

```typescript
type TemplateStudioVM = {
  studioState: Signal<StudioState>;
  draft: Signal<{ corpo: string; versao: number } | null>;
  error: Signal<AppError | null>;
};
// eventos UI: onCompose({ brief, contexto, assetOrigemId? }), onAceitarRascunho(), onEditarManual()
```

## Regras de roteamento — `RoutingRulesVM`

```typescript
type RoutingRulesVM = {
  regras: Signal<RegraRoteamentoVM[]>;   // ordenadas por prioridade
  loading: Signal<boolean>;
  error: Signal<AppError | null>;
};
// eventos UI: onNova(), onEditar(id), onSave(regra)
```

## Mensagens (lista) — `MessagesListVM`

```typescript
type MessagesListVM = {
  items: Signal<MensagemResumoVM[]>;
  loading: Signal<boolean>;
  error: Signal<AppError | null>;
  filtro: Signal<{ leadId?: string; canal?: Canal; estado?: EstadoEntrega; desde?: string; ate?: string }>;
  page: Signal<{ index: number; size: number; total: number }>;
};
// eventos UI: onFilterChange(f), onOpen(id), onDispatch({ templateId, leadId, variaveis, canal? })
```

## Mensagem (detalhe + rastreio) — `MessageDetailVM`

```typescript
type MessageDetailVM = {
  mensagem: Signal<MensagemVM | null>;
  eventos: Signal<EventoEntregaVM[]>;     // append-only, alimentado por polling
  estadoTerminal: Signal<boolean>;        // computed: LIDA | FALHADA -> para o polling (ADR-005)
  polling: Signal<boolean>;
  error: Signal<AppError | null>;
};
// eventos UI: onRefresh(), (ciclo de vida do polling controlado pela page: startPolling/stopPolling)
```

## Config de canal — `ChannelConfigVM`

```typescript
type ChannelConfigVM = {
  canais: Signal<ConfigCanalVM[]>;
  loading: Signal<boolean>;
  error: Signal<AppError | null>;
};
// eventos UI: onNovo(), onEditar(id), onSave({ canal, provedor, identidadeRemetente, credencialRef, janelaEnvio? })
```

## Critérios de aceite (EARS)

- **C-03.1 (Ubiquitous):** `THE SYSTEM SHALL expor todo estado de tela como Signal somente-leitura a partir das facades`
- **C-03.2 (State-driven):** `WHILE o canal é EMAIL, THE SYSTEM SHALL marcar assuntoObrigatorio como verdadeiro e exigir assunto não-vazio antes de salvar`
- **C-03.3 (Event-driven):** `WHEN o corpo do template muda, THE SYSTEM SHALL recomputar variaveisInvalidas e bloquear o salvamento enquanto houver placeholders não declaradas`
- **C-03.4 (Event-driven):** `WHEN o estado de entrega da mensagem atinge LIDA ou FALHADA, THE SYSTEM SHALL marcar estadoTerminal como verdadeiro`
- **C-03.5 (Ubiquitous):** `THE SYSTEM SHALL derivar acoesDisponiveis do template a partir do estado e das permissões comm nunca exibindo ação não permitida`

## Referências

- `03-domain-framing-frontend.md` (VMs base + invariantes) · SPEC-04 (data-access) · ADR-002 / ADR-005
