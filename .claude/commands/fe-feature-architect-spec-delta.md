# FE Feature Architect -- Spec Delta (Journey OS)

Voce e o agente que aplica **diffs cirurgicos** em SPECs e generator-config.yml de um
modulo para acomodar uma feature nova.

**Args:** `$ARGUMENTS` -- formato: `<MODULO> <feature-slug>`

---

## Papel do agente

Voce e a **etapa 2** da pipeline `fe-feature-architect-*`. Le o `conformance-report.md`
do `discover` e aplica as alteracoes documentais (SPECs + generator-config + .feature
files + ADR stubs) em modo delta.

Pipeline:
1. fe-feature-architect-from-prototype (opcional)
2. fe-feature-architect-discover
3. **fe-feature-architect-spec-delta** (voce)
4. fe-feature-architect-backlog
5. fe-feature-architect-scaffold

---

## Principio central

Delta e cirurgico. Nao reescrever SPECs inteiros -- apenas adicionar linhas/secoes nas
posicoes indicadas pelo `conformance-report.md`. Cada arquivo modificado e auditavel
via `spec-delta.md` (manifesto do que foi tocado).

Se conformance-report status = ❌ Violador: **bloqueia** ate o usuario confirmar
criacao de ADR-novo (proceder so com `proposed`).

---

## Pre-requisitos (bloqueadores)

```
docs/architecture/frontend/modules/<modulo>/frontend/frontend-spec/features/<feature-slug>/conformance-report.md
docs/architecture/frontend/modules/<modulo>/frontend/frontend-spec/SPEC-01..08.md
docs/architecture/frontend/modules/<modulo>/frontend/frontend-spec/generator-config.yml
```

### Bloqueio

- Status do report = ❌ Violador -> bloqueado ate decisao explicita do usuario sobre ADR-novo
- Faltam SPECs base -> retornar a `/fe-planner <MODULO>` para gerar SPECs do modulo

---

## Delta deterministico (spec-delta-diff, D-321)

Antes de aplicar, precomputar o delta codigo×SPEC (read-only) e **curar o resultado**:

```bash
python scripts/spec-delta-diff.py diff --module <MODULO> --report
```

Escreve `<MODULO>.spec-delta.json` (`specRequiresMissing`, `codeHasUnspecced`,
`routeMismatch`, `summary`). Consome o inventario do `fe-discover-scan` (D-320). Use-o
como ponto de partida para as secoes abaixo, confirmando cada divergencia.

## O que aplicar (por SPEC do modulo)

### SPEC-01 -- route-map

Adicionar linha na tabela mestre:

```markdown
| Path                                | Component               | Feature Lib                                         | Guards                                       | Title              | Breadcrumb     |
|-------------------------------------|-------------------------|-----------------------------------------------------|----------------------------------------------|--------------------|----------------|
| `/<modulo>/<feature-slug>`          | `<Slug>PageComponent`   | `frontend/libs/<modulo>/feature-<feature-slug>/`    | `[authGuard, empresaGuard, accessGuard(<perm>)]` | `<Titulo Feature>` | `<Slug>`       |
```

Lazy obrigatorio:
```ts
loadComponent: () => import('@journeyos/<modulo>/feature-<feature-slug>').then(m => m.<Slug>PageComponent)
```

### SPEC-02 -- component-hierarchy

Anexar arvore ASCII apos a ultima feature listada. Se houve `--from-prototype`,
copiar a arvore de `prototypes/<modulo>/<feature-slug>/draft-spec-02-component-hierarchy.md`.

### SPEC-03 -- view-models

Adicionar VMs como `Readonly` types TypeScript. Naming: `<Slug><Role>VM`.

```ts
export type <Slug>ListItemVM = Readonly<{
  id: string;
  // campos derivados do DTO BE
}>;

export type <Slug>DetailVM = Readonly<{
  id: string;
  // ...
}>;

export type <Slug>FormVM = Readonly<{
  // shape do formulario reativo
}>;
```

UI events:
- `<slug>.list.itemSelected` -- payload: `{ id: string }`
- `<slug>.detail.formSubmitted` -- payload: `<Slug>FormVM`

### SPEC-04 -- data-access

Adicionar resource (so se feature requer dados novos):

```markdown
| Resource     | Endpoint base                          | Operations                      | Service                  | Facade               | Cache       |
|--------------|----------------------------------------|---------------------------------|--------------------------|----------------------|-------------|
| `<Resource>` | `/api/<microservico>/<resource>`       | list, getById, create, update   | `<Resource>ApiService`   | `<Resource>Facade`   | per-nav     |
```

Microservico = nome do servico backend que expoe o endpoint (ex.: `<module>`, `<module>`,
`<module>`, `<module>`, `<module>`, `<module>`, `<module>`, `iam`).

### SPEC-05 -- permissions

Adicionar permission keys novas em `<modulo>.permission-map.ts`:

```ts
export const <Modulo>Permissions = {
  // ... existentes
  '<modulo>.<feature-slug>.read':  '<Permissao legivel humana>',
  '<modulo>.<feature-slug>.write': '<Permissao legivel humana>',
} as const;
```

### SPEC-06 -- empresa-context

So mexer se a feature tem comportamento especial multi-empresa (raro). Casos:
- feature precisa cruzar dados de >1 empresa (deve passar por endpoint BE dedicado)
- feature tem widget que mostra agregado de todas as empresas (relatorio consolidado)

Default: feature opera na empresa ativa via interceptor automatico -- nada a documentar aqui.

### SPEC-07 -- error-handling

Adicionar mappings novos `ProblemDetail` -> `AppError` so se a feature consome erros
nao previstos. Ex.: regra de negocio especifica do BE (`409 Conflict` com `type:
"comercial.orcamento.bloqueado-por-credito"`).

### SPEC-08 -- e2e-scenarios

Adicionar cenarios Gherkin:
- happy-path
- error-recovery (uma falha tipica + retry)
- entitlement-denied (se feature exigir permission especifica -- quase sempre)
- multi-empresa-switch (se feature precisa funcionar apos troca de empresa)

### .feature files

Para cada cenario novo, criar arquivo:

```
frontend/apps/journey-os-web-e2e/src/specs/<modulo>/<feature-slug>-<cenario>.feature
```

### generator-config.yml

Aplicar diff exatamente como apresentado no `conformance-report.md` §5.

```yaml
features:
  - name: <feature-slug>
    routes:
      - path: <feature-slug>
        component: <Slug>PageComponent
    components:
      - <Slug>PageComponent
      - <Slug>ListComponent
      - <Slug>DetailComponent
    permissions:
      - <modulo>.<feature-slug>.read
      - <modulo>.<feature-slug>.write

# se resource novo:
data_access:
  resources:
    - name: <Resource>
      endpoint: /api/<microservico>/<resource>
      operations: [list, getById, create, update]
```

### ADR novo (se conformance-report indicou)

Criar stub em `docs/architecture/frontend/adr/ADR-00N-<topic>.md`:

```markdown
# ADR-00N -- <Titulo>

- **Status:** proposed
- **Data:** YYYY-MM-DD
- **Issue relacionada:** <MODULO>-FE-NNN (a ser criada por backlog)
- **Autores:** [pendente]
- **Supersedes:** -- (ou cita ADR superseded se aplicavel)

---

## Contexto

<motivacao extraida do conformance-report §2>

## Decisao

<decisao explicita -- evita interpretacao>

## Alternativas consideradas

- <A>
- <B>

## Consequencias

### Positivas
- ...

### Negativas
- ...

## Referencias

- conformance-report: `docs/architecture/frontend/modules/<modulo>/frontend/frontend-spec/features/<feature-slug>/conformance-report.md`
- spec-delta: `docs/architecture/frontend/modules/<modulo>/frontend/frontend-spec/features/<feature-slug>/spec-delta.md`
```

Atualizar `docs/architecture/frontend/adr/README.md` (indice) com entrada nova `proposed`.

---

## Manifesto de delta

Apos aplicar todas as mudancas, gerar `spec-delta.md` no mesmo diretorio do conformance-report:

```markdown
# Spec Delta -- <feature-slug>

**Modulo:** <MODULO>
**Data:** YYYY-MM-DD
**Conformance report:** `./conformance-report.md`

## Arquivos modificados

| Arquivo | Tipo | Linhas |
|---|---|---|
| modules/<modulo>/frontend/frontend-spec/SPEC-01-route-map.md | modified | +1 |
| modules/<modulo>/frontend/frontend-spec/SPEC-02-component-hierarchy.md | modified | +12 |
| modules/<modulo>/frontend/frontend-spec/SPEC-03-view-models.md | modified | +8 |
| modules/<modulo>/frontend/frontend-spec/SPEC-04-data-access.md | modified | +1 |
| modules/<modulo>/frontend/frontend-spec/SPEC-05-permissions.md | modified | +2 |
| modules/<modulo>/frontend/frontend-spec/SPEC-08-e2e-scenarios.md | modified | +6 |
| modules/<modulo>/frontend/frontend-spec/generator-config.yml | modified | +14 |

## Arquivos criados

| Arquivo | Tipo |
|---|---|
| frontend/apps/journey-os-web-e2e/src/specs/<modulo>/<feature-slug>-happy-path.feature | new |
| frontend/apps/journey-os-web-e2e/src/specs/<modulo>/<feature-slug>-error-recovery.feature | new |
| docs/architecture/frontend/adr/ADR-00N-<topic>.md (se aplicavel) | new |

## Diff resumido

### SPEC-01-route-map.md
- Linha N: nova rota `<feature-slug>` adicionada na tabela mestre.

### SPEC-02-component-hierarchy.md
- Linha M: arvore `feature-<feature-slug>` anexada apos `feature-<vizinha>`.

### generator-config.yml
- Bloco `features:` ganhou entrada `<feature-slug>`.
- Bloco `data_access.resources:` ganhou entrada `<Resource>` (se aplicavel).
```

---

## NAO fazer

- nao reescrever SPECs do zero -- so anexar/modificar
- nao tocar em SPECs nao listados no `conformance-report.md`
- nao gerar codigo TS/Angular
- nao criar issues (responsabilidade de `backlog`)
- nao alterar status de ADR existente para `accepted` -- promocao e decisao humana
- nao prosseguir se conformance-report = ❌ Violador sem decisao explicita

---

## Saida final obrigatoria

```
Spec delta aplicado para <MODULO>/<feature-slug>

Arquivos modificados:
- modules/<modulo>/frontend/frontend-spec/SPEC-01-route-map.md (+N)
- modules/<modulo>/frontend/frontend-spec/SPEC-02-component-hierarchy.md (+M)
- modules/<modulo>/frontend/frontend-spec/SPEC-03-view-models.md (+P)
- modules/<modulo>/frontend/frontend-spec/SPEC-04-data-access.md (+Q) [se aplicavel]
- modules/<modulo>/frontend/frontend-spec/SPEC-05-permissions.md (+R)
- modules/<modulo>/frontend/frontend-spec/SPEC-08-e2e-scenarios.md (+S)
- modules/<modulo>/frontend/frontend-spec/generator-config.yml (+T)

Arquivos criados:
- frontend/apps/journey-os-web-e2e/src/specs/<modulo>/<feature-slug>-happy-path.feature
- frontend/apps/journey-os-web-e2e/src/specs/<modulo>/<feature-slug>-error-recovery.feature
- docs/architecture/frontend/adr/ADR-00N-<topic>.md (status proposed) [se aplicavel]
- modules/<modulo>/frontend/frontend-spec/features/<feature-slug>/spec-delta.md (manifesto)

Proxima acao:
-> /fe-feature-architect-backlog <MODULO> <feature-slug>
```
