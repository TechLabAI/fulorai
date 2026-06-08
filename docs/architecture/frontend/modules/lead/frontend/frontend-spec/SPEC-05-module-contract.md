# SPEC-05 — Module Contract — LEAD · Frontend

> Conteúdo de `libs/lead/shell-entry/lead.contract.ts` (+ permission-map + feature-flags). Define como
> o Shell descobre menu, rotas, permissões e flags do LEAD.

## `lead.contract.ts`

```typescript
export const MODULE_KEY = 'lead';

export const MODULE_MENU_METADATA: ModuleMenuMetadata = {
  key: MODULE_KEY,
  label: 'Leads',
  route: '/lead/leads',
  icon: 'groups',
  deepLinks: [
    { key: 'maturity',      label: 'Maturity Score', route: '/lead/maturity',      perm: 'lead.lead.read' },
    { key: 'segments',      label: 'Segmentos',      route: '/lead/segments',      perm: 'lead.segment.read' },
    { key: 'surveys',       label: 'Surveys',        route: '/lead/surveys',       perm: 'lead.survey.read' },
    { key: 'qualification', label: 'Regras',         route: '/lead/qualification', perm: 'lead.qualification.read' },
  ],
};
```

## `lead.permission-map.ts`

Mapeia rota/ação → permissão canônica (espelha o BE `api-contract.md`). Cada permissão justificada:

| Permissão | Onde | Justificativa |
|---|---|---|
| `lead.lead.read` | fila, detalhe, maturity | leitura de leads e score (SDR + growth). |
| `lead.lead.criar` | (ação, captura mediada) | criação de lead — no MVP a captura é mediada pelo BE/integrações; permissão reservada para ações manuais. |
| `lead.lead.editar` | detalhe (editar perfil) | edição de atributos do perfil. |
| `lead.lead.anonimizar` | detalhe (LGPD) | anonimização (terminal) — ação sensível. |
| `lead.lead.expurgar` | detalhe (LGPD) | expurgo físico (right to be forgotten) — ação sensível. |
| `lead.survey.read` | surveys | leitura de surveys. |
| `lead.survey.criar` / `lead.survey.editar` | surveys (editor) | definição/edição de surveys. |
| `lead.survey.responder` | detalhe / captura | submeter respostas para um lead. |
| `lead.qualification.read` | regras | leitura de versões de regra. |
| `lead.qualification.criar` | regras (editor) | criar nova versão (inativa). |
| `lead.qualification.ativar` | regras | ativar uma versão (governança). |
| `lead.qualification.executar` | detalhe (requalificar) | forçar recálculo de um lead. |
| `lead.segment.read` | segmentos | leitura de segmentos + fila por segmento. |
| `lead.segment.criar` / `lead.segment.editar` / `lead.segment.excluir` | segmentos (editor) | CRUD de segmentos. |

## `lead.feature-flags.ts`

```typescript
export const MODULE_FEATURE_FLAGS: ModuleFeatureFlags = {
  'lead.maturity-score':      { defaultState: 'enabled' },
  'lead.qualification-rules': { defaultState: 'enabled' },
};
```

Justificativa das flags:
- **`lead.maturity-score`** (`enabled`) — permite desligar o dashboard de distribuição/radar sem afetar
  a fila/detalhe; útil se um tenant ainda não usa o módulo de score agregado.
- **`lead.qualification-rules`** (`enabled`) — permite ocultar a governança de regras (operação só
  consome scores prontos) sem afetar leitura/segmentação.

> O badge `assistIa` **não** é flag — é sempre exibido (transparência do score, ADR-005).

## Critérios de aceite (EARS)

- `THE SYSTEM SHALL expose MODULE_MENU_METADATA with route /lead/leads as the LEAD entry point.`
- `WHERE a deep link declares a permission, THE SYSTEM SHALL show that deep link only to users who hold the permission.`
- `WHILE the feature flag lead.qualification-rules is disabled, THE SYSTEM SHALL hide the "Regras" deep link and block its route.`
- `THE SYSTEM SHALL define a default state for every feature flag in MODULE_FEATURE_FLAGS.`

## Referências
- `04-frontend-architecture-direction.md` §7 · `SPEC-06-shell-integration.md` · BE `api-contract.md`
