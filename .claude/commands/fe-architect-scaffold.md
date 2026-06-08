# FE Architect (Journey OS) -- Scaffold

Voce e o agente de scaffold de codigo para um módulo nova no Journey OS frontend.

**Module prefix:** `$ARGUMENTS`

Se nao informado, perguntar: `Qual o prefixo do módulo? (ex.: WRKS | LEAD | JRNY | ASST | COMM | SALE | INTL | GWY | REG | MIG | ...)`

---

## Papel do agente

Voce orquestra a geracao do esqueleto **executavel** da tool FE invocando
o plugin Nx interno `@hub/internal`. Apos voce, o pipeline padrao
(`fe-validator -> fe-planner -> fe-implement` ou `journey-os-tools-*`) assume.

Voce **NAO** gera arquivos Angular/SCSS/JSON manualmente. O plugin faz tudo:
- `apps/<tool>/` com tool-module canonico (tool.contract, tool.routes, tool.module, tool.permission-map, tool.feature-flags, tool.bootstrap, tool.nav.config)
- `libs/<tool>/feature-<X>/` por feature declarada
- `libs/<tool>/data-access/` com services + facades signals-based
- `libs/<tool>/access/` com guards
- `libs/<tool>/integration/` com `ToolShellIntegrationService`
- `libs/<tool>/navigation/` com breadcrumb state
- Registro em `apps/shell/src/app/config/tool-descriptors.ts` + `shell-routes.ts`
- `apps/<tool>-e2e/` com Playwright specs derivados de `.feature`
- Tags Nx (scope + type) corretas em todos os `project.json`

Pipeline:
1. fe-architect-vision (concluida)
2. fe-architect-specs (concluida)
3. fe-architect-backlog (concluida)
4. **fe-architect-scaffold** (voce)
5. /project:fe-validator <ISSUE_ID> (pipeline padrao)

---

## Principio central

Scaffold nao implementa logica. Compila, registra app+libs no Nx workspace,
satisfaz boundary rules e deixa a tool pronta para o `fe-implement` da P1.

A geracao e **document-driven**: o plugin le `docs/architecture/frontend/modules/<tool>/frontend/frontend-spec/generator-config.yml` e deriva tudo de la.

---

## Pre-requisitos

### Obrigatorios (bloqueiam se ausentes)

```
docs/architecture/frontend/modules/<tool>/_brief.md
docs/architecture/frontend/modules/<tool>/frontend/frontend-spec/generator-config.yml
docs/architecture/frontend/modules/<tool>/frontend/frontend-spec/SPEC-01..08
docs/architecture/frontend/modules/<tool>/frontend/issues/FE-<PREFIX>-001.md
```

### Recomendados

```
docs/architecture/frontend/modules/<tool>/frontend/contracts/backend-api-cross-link.md
docs/architecture/frontend/modules/<tool>/frontend/e2e/*.feature   (>= 1 para e2e generator gerar specs reais)
```

### Bloqueio

Se faltar qualquer obrigatorio:

```
Scaffold nao pode ser gerado: documentacao incompleta.
Faltando: <lista>
-> retornar a /project:fe-architect-{vision|specs|backlog} <PREFIX>
```

---

## Execucao

### 1. Resolver caminho da tool

A partir do `<PREFIX>` informado, derivar o nome canonico:
- ler `docs/architecture/frontend/modules/<lowercase-name>/frontend/frontend-spec/generator-config.yml`
- campo `service:` confirma o nome canonico

### 2. Dry-run (recomendado em primeira execucao)

```bash
npx nx g @hub/internal:tool --name=<tool> --dry-run
```

Analisar o output: lista de arquivos a serem criados. Confirmar com o usuario antes de executar de verdade.

### 3. Geracao real

```bash
npx nx g @hub/internal:tool --name=<tool>
```

Flags adicionais quando aplicaveis:
- `--force` para sobrescrever arquivos existentes (re-execucao)
- `--specPath=<path>` para override do path dos docs

### 4. Verificacao pos-scaffold

```bash
# Lint (Nx boundaries + ESLint custom)
npx nx lint <tool>
npx nx lint apps/<tool>
# ou em batch:
npx nx affected -t lint --base=HEAD~1

# Test (Jest unit)
npx nx test <tool>
npx nx affected -t test --base=HEAD~1

# Build (sem erros TS)
npx nx build <tool>
npx nx build shell
```

Os 3 obrigatorios verdes antes de finalizar:
- `nx lint <tool>` (RULE: boundary tags + standalone + OnPush + Signals)
- `nx test <tool>` (Jest passa, mesmo que ainda sem testes funcionais)
- `nx build <tool>` (TypeScript compila sem erros)

**Nao executar e2e aqui** -- responsabilidade do `fe-implement` na onda P9.

Se `nx lint` falhar:
- inspecionar erro
- verificar se `generator-config.yml` esta consistente com docs
- corrigir e regerar com `--force`

### 5. Reportar arquivos criados

O plugin imprime estatisticas (apps + libs + total). Repassar ao usuario o resumo + comando de proxima acao.

---

## NAO fazer

- nao gerar arquivos Angular/SCSS/TS manualmente -- responsabilidade do plugin
- nao alterar arquivos gerados antes do `fe-validator` consolidar
- nao implementar logica de negocio (delegar ao `fe-implement P1+`)
- nao executar testes e2e (apenas `nx lint` + `nx test` + `nx build`)
- nao mexer em `apps/<tool>/` ou `libs/<tool>/*` se ja foi gerado em sessao anterior -- usar `--force` se necessario regerar
- nao alterar o padrao tax-map (CLAUDE.md §14) sem ADR aceito

---

## Saida final obrigatoria

```
Scaffold gerado para <PREFIX>

Tool criada:
  App:  apps/<tool>/
  Libs: libs/<tool>/{access,data-access,feature-<X>,integration,navigation}/
  e2e:  apps/<tool>-e2e/

Pacote base: @<tool>/* (path mappings em tsconfig.base.json)

Registro:
  apps/shell/src/app/config/tool-descriptors.ts (entry adicionada)
  apps/shell/src/app/router/shell-routes.ts (toolChildRoutes[] atualizado)

Arquivos:
  apps/<tool>/: <N> files
  libs/<tool>/: <M> files (em <K> sublibs)
  e2e: <P> Playwright specs

Verificacao:
  nx lint:  OK (boundaries + standalone + OnPush + Signals + tax-map structure)
  nx test:  OK (Jest unit, sem testes funcionais ainda)
  nx build: OK (TypeScript compila)

Proxima acao (pipeline padrao):
-> /project:fe-validator <FE-<PREFIX>-001>
```
