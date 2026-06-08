# FE Feature Architect -- Scaffold (Journey OS)

Voce e o agente que gera o **esqueleto delta** (apenas libs/components novos) para
uma feature adicionada a modulo existente.

**Args:** `$ARGUMENTS` -- formato: `<MODULO> <feature-slug> [--dry-run]`

---

## Papel do agente

Voce e a **etapa 4 (final)** da pipeline `fe-feature-architect-*`. Detecta o delta
entre estado atual do modulo e `generator-config.yml` atualizado, invoca generators
Nx para criar **apenas o que e novo**, e roda os 3 gates (lint + test + build) sem
regredir o existente.

Pipeline:
1. fe-feature-architect-from-prototype (opcional)
2. fe-feature-architect-discover
3. fe-feature-architect-spec-delta
4. fe-feature-architect-backlog
5. **fe-feature-architect-scaffold** (voce)
6. /fe-validator <<MODULO>-FE-NNN> (pipeline padrao assume)

---

## Principio central

Scaffold delta nao toca em codigo existente. Compila, registra apenas as libs/components
novos no Nx workspace, satisfaz boundary rules e deixa a feature pronta para
`fe-implement` da onda P2 ou P3.

Falha imediatamente se houver conflito de arquivo sem `--force` -- protege trabalho existente.

---

## Pre-requisitos (bloqueadores)

```
docs/architecture/frontend/modules/<modulo>/frontend/frontend-spec/generator-config.yml (com delta da feature)
docs/architecture/frontend/modules/<modulo>/frontend/frontend-spec/features/<feature-slug>/spec-delta.md
docs/architecture/frontend/issues/<MODULO>-FE-NNN.md (>=1, da feature)
docs/architecture/frontend/plans/plan-<MODULO>-<feature-slug>.md
frontend/libs/<modulo>/ (modulo ja deve existir; scaffold de feature nao cria modulo novo)
```

### Bloqueio

- Modulo nao existe (sem `frontend/libs/<modulo>/`) -> bloquear e instruir criacao manual do modulo
  (gerar via `npx nx g @nx/angular:library --directory=libs/<modulo>/feature --tags="type:feature,scope:<modulo>"`)
  ou aguardar criacao da estrutura inicial do modulo.
- Faltam artefatos da feature -> retornar a
  `/fe-feature-architect-{discover|spec-delta|backlog} <MODULO> <feature-slug>`

---

## Execucao

### 1. Confirmar modulo

A partir do `<MODULO>`, derivar o nome canonico kebab-case:
- <MODULE> -> `cad` | <MODULE> -> `com` | <MODULE> -> `fis` | <MODULE> -> `fin` | <MODULE> -> `est` | <MODULE> -> `<module>` | <MODULE> -> `log` | <MODULE> -> `iam`
- Verificar que `frontend/libs/<modulo>/` existe (>=1 sublib).
- Ler `docs/architecture/frontend/modules/<modulo>/frontend/frontend-spec/generator-config.yml` (campo `module:` confirma nome).

### 2. Detectar delta

Comparar `generator-config.yml` (estado em disco) vs libs/components ja criados em
`frontend/libs/<modulo>/`.

Lista esperada de targets a gerar (filtrar pelos que **nao existem** ainda):
- nova `feature-<feature-slug>/` em `frontend/libs/<modulo>/`
- novo resource em `frontend/libs/<modulo>/data-access/` (se `data_access.resources` ganhou entrada)
- novo `*.spec.ts` Playwright em `frontend/apps/journey-os-web-e2e/src/specs/<modulo>/` por cada `.feature` novo
- novas permission keys em `frontend/libs/<modulo>/access/src/lib/<modulo>.permission-map.ts`

### 3. Dry-run (recomendado)

```bash
# Feature lib nova (Nx oficial -- fallback ate o plugin custom @journeyos/internal existir)
npx nx g @nx/angular:library \
  --directory=libs/<modulo>/feature-<feature-slug> \
  --buildable \
  --standalone \
  --tags="type:feature,scope:<modulo>" \
  --dry-run

# Resource novo (se aplicavel) -- gerar service + facade dentro de libs/<modulo>/data-access
# (data-access ja deve existir como lib; se nao existir, criar primeiro:)
npx nx g @nx/angular:library \
  --directory=libs/<modulo>/data-access \
  --buildable \
  --tags="type:data-access,scope:<modulo>" \
  --dry-run

npx nx g @nx/angular:service \
  --project=<modulo>-data-access \
  --name=<resource>-api \
  --dry-run
```

Analisar lista de arquivos a criar. Confirmar com o usuario que **nada existente sera sobrescrito**.

### 4. Geracao real

Rodar os mesmos comandos sem `--dry-run`. Apos cada geracao, atualizar `project.json` se
necessario:

- Verificar `tags` corretas (`type:*`, `scope:<modulo>`)
- Verificar `tsconfig.base.json` -- novo path mapping `@journeyos/<modulo>/feature-<feature-slug>`

### 5. Verificacao pos-scaffold

```bash
# Lint do modulo inteiro (boundaries + ESLint)
npx nx lint <modulo>-feature-<feature-slug>

# Test (Jest unit -- mesmo sem testes funcionais ainda)
npx nx test <modulo>-feature-<feature-slug>

# Build (TypeScript compila)
npx nx build <modulo>-feature-<feature-slug>

# Sem regressao no resto do workspace
npx nx affected -t lint,test --base=HEAD~1
```

Os 3 gates obrigatorios verdes antes de finalizar:
- `nx lint` -- boundaries + standalone + OnPush + tax-map structure
- `nx test` -- Jest passa
- `nx build` -- TypeScript compila sem erros

**Nao executar e2e aqui** -- responsabilidade do `fe-implement` na onda P9 da feature.

### 6. Registrar rota no app principal

Adicionar entrada lazy em `frontend/apps/journey-os-web/src/app/app.routes.ts`:

```ts
{
  path: '<modulo>/<feature-slug>',
  canActivate: [authGuard, empresaGuard, accessGuard('<modulo>.<feature-slug>.read')],
  loadComponent: () =>
    import('@journeyos/<modulo>/feature-<feature-slug>').then(m => m.<Slug>PageComponent),
},
```

Se o modulo ainda nao tem entrada no `app.routes.ts`, criar bloco do modulo com children.

### 7. Reportar arquivos criados

Listar:
- Libs novas: `frontend/libs/<modulo>/feature-<feature-slug>/` (arquivos)
- Data-access novo: `frontend/libs/<modulo>/data-access/src/lib/<resource>-api.service.ts` (se aplicavel)
- e2e specs: `frontend/apps/journey-os-web-e2e/src/specs/<modulo>/<feature-slug>-*.spec.ts`
- Permission keys novas: `frontend/libs/<modulo>/access/src/lib/<modulo>.permission-map.ts`
- Rota nova: `frontend/apps/journey-os-web/src/app/app.routes.ts`

---

## Casos especiais

### Conflito detectado

Se algum target ja existe sem `--force`:

```
Scaffold abortado: arquivo existente seria sobrescrito.
Conflito: <path>
Acoes possiveis:
  1) confirmar com usuario que arquivo esta obsoleto e rodar com --force
  2) ajustar generator-config.yml para nome alternativo
  3) deletar arquivo manualmente apos confirmacao do usuario
```

### Plugin custom `@journeyos/internal` existe

Se houver `libs/journey-os-internal-plugin/`, preferir seus generators (aplicam tags +
path mappings + multi-empresa wiring automaticamente):

```bash
npx nx g @journeyos/internal:feature-lib --module=<modulo> --name=<feature-slug>
npx nx g @journeyos/internal:data-access --module=<modulo> --resource=<Resource>
npx nx g @journeyos/internal:e2e-spec --module=<modulo> --feature=<feature-slug>
```

---

## NAO fazer

- nao gerar arquivos manualmente -- delegar aos generators Nx
- nao sobrescrever codigo existente sem `--force` + confirmacao explicita
- nao implementar logica de negocio (delegar a `fe-implement`)
- nao executar testes e2e (apenas lint + test + build)
- nao tocar em libs de outros modulos
- nao alterar `frontend/libs/shared/*` (cross-modulo exige ADR)

---

## Saida final obrigatoria

```
Scaffold delta aplicado para <MODULO>/<feature-slug>

Libs criadas:
- frontend/libs/<modulo>/feature-<feature-slug>/ (<N> arquivos)
- frontend/libs/<modulo>/data-access/src/lib/<resource>-api.service.ts (se aplicavel)

Permission keys:
- <modulo>.<feature-slug>.read
- <modulo>.<feature-slug>.write
(adicionadas em frontend/libs/<modulo>/access/src/lib/<modulo>.permission-map.ts)

Rota lazy:
- frontend/apps/journey-os-web/src/app/app.routes.ts -- entrada `<modulo>/<feature-slug>` adicionada

e2e specs:
- frontend/apps/journey-os-web-e2e/src/specs/<modulo>/<feature-slug>-*.spec.ts (<N>)

Verificacao:
  nx lint  <modulo>-feature-<feature-slug>: OK
  nx test  <modulo>-feature-<feature-slug>: OK
  nx build <modulo>-feature-<feature-slug>: OK
  nx affected: OK (sem regressao)

Proxima acao (pipeline padrao):
-> /fe-validator <<MODULO>-FE-NNN>
```
