# SPEC-05 — Module Contract — INTL

> Conteúdo de `libs/intl/shell-entry/src/lib/intl.contract.ts` (+ permission-map + feature-flags).
> Consumido pelo Shell via `INTL_MODULE_DESCRIPTOR` (`@journeyos/intl`).

```typescript
export const MODULE_KEY = 'intl' as const;

export const MODULE_MENU_METADATA: ModuleMenuMetadata = {
  key: MODULE_KEY,
  label: 'Inteligência',
  route: '/intl/copilot',
  icon: 'auto_awesome',
  deepLinks: [
    { label: 'Copilot',      route: '/intl/copilot',    permission: 'intl.copilot.use' },
    { label: 'Conhecimento', route: '/intl/knowledge',  permission: 'intl.knowledge.read' },
    { label: 'Analítica',    route: '/intl/analytics',  permission: 'intl.analytics.read' },
  ],
};

export const INTL_PERMISSION_MAP: ModulePermissionMap = {
  'intl.copilot.use':     [],   // papéis preenchidos pela Access Layer (WRKS) — vazio = derivado do BE
  'intl.copilot.read':    [],
  'intl.knowledge.read':  [],
  'intl.knowledge.write': [],
  'intl.analytics.read':  [],
};

export const INTL_FEATURE_FLAGS: ModuleFeatureFlags = {
  'intl.copilot':           { defaultState: 'enabled' },
  'intl.knowledge':         { defaultState: 'enabled' },
  'intl.analytics':         { defaultState: 'enabled' },
  'intl.copilot-streaming': { defaultState: 'disabled' },  // reservado pós-MVP (ADR-005)
};
```

## Justificativa das permissões

| Permissão | Por quê | Endpoints |
|---|---|---|
| `intl.copilot.use` | Abrir conversa e perguntar (operação ativa do copiloto). | `POST /copilot/conversas`, `.../perguntar` |
| `intl.copilot.read` | Ler histórico de conversa (leitura separada da escrita). | `GET /copilot/conversas/{id}` |
| `intl.knowledge.read` | Listar/buscar/ver nós (curadoria — leitura). | `GET /knowledge/nos`, `/{id}` |
| `intl.knowledge.write` | Criar/editar/indexar/arquivar nós. | `POST/PUT/DELETE /knowledge/nos...` |
| `intl.analytics.read` | Ler dashboards (funil, uso do copiloto) — tudo read-only. | `GET /analytics/**` |

> As permissões espelham 1:1 o `api-contract.md` do BE. O mapeamento papel→permissão é **derivado
> da Access Layer (WRKS)**, não hard-coded aqui (`[]` = resolvido pelo BE/AccessDecision).

## Justificativa das feature-flags

| Flag | defaultState | Motivo |
|---|---|---|
| `intl.copilot` | enabled | Feature núcleo do MVP. |
| `intl.knowledge` | enabled | Feature núcleo do MVP (alimenta o copiloto). |
| `intl.analytics` | enabled | Feature núcleo do MVP (read-only). |
| `intl.copilot-streaming` | **disabled** | Streaming SSE diferido — sem endpoint no BE (ADR-005); flag pronta para ativação por ADR futuro. |

## Critérios de aceite (EARS)

- `THE SYSTEM SHALL expose the INTL menu entry "Inteligência" routed to /intl/copilot gated by intl.copilot.use.`
- `THE SYSTEM SHALL filter each INTL deep link by its permission via NavigationService and AccessDecisionService.`
- `WHILE the intl.analytics flag is disabled, THE SYSTEM SHALL omit the Analítica route and its menu entry.`
- `WHERE the intl.copilot-streaming flag is enabled, THE SYSTEM SHALL use streaming; otherwise THE SYSTEM SHALL render request and response answers.`
- `THE SYSTEM SHALL resolve role-to-permission mapping from the Access Layer and SHALL NOT hard-code roles in the module contract.`
