# Catálogo de Permissões — Journey OS

> Lista canônica de permissões namespace `<modulo>.<recurso>.<acao>`.
> Aplicada em V1 do `journey-os-migrations` (tabela `journeyos_global.permissao`).
> Bundle por papel: [`papeis.md`](papeis.md).
>
> **Fonte de verdade:** `templates/architecture/decisions/permission-catalogue.arch.json` (D-060).
> Este markdown é gerado deterministicamente. Não editar à mão — o próximo render sobrescreve.

## Convenções

- **Namespace de 3 partes (regra geral):** `<modulo>.<recurso>.<acao>` (snake/kebab-case, sempre lowercase).
- **4 partes** quando o recurso tem sub-recurso natural (ex: `cad.vendedor.comissao.config`).
- **Módulos** (prefixos canônicos): `wrks, lead, jrny, asst, comm, sale, intl, gwy, reg, mig`.
- **Ações canônicas**: `read`, `criar`, `editar`, `excluir`, `cancelar`, `aprovar`, `emitir`, etc. (verbos do domínio em pt-BR — ver `arch_decisions._OP_VERB_TO_ACTION` para o mapeamento `op-name → ação`).
- **Wildcards proibidos em produção** — uma linha por permissão (auditoria precisa rastrear).

## WRKS — Workspace & Identity

Multi-tenancy, business units, teams, users, RBAC, administration

```
```

## LEAD — Lead Intelligence & Qualification

Leads, perfil, segmentação, Maturity Score (6D), surveys, qualification rules

```
```

## JRNY — Journey & Routing

Jornadas, estágios, Journey Builder, Routing Engine, decision log

```
```

## ASST — Asset Hub

Assets, Asset Studio, versionamento, approval workflow, Asset Intelligence

```
```

## COMM — Communication Hub

WhatsApp/Email/Telegram/SMS via integração, templates, message routing

```
```

## SALE — Sales & Revenue

CRM (pipeline/SDR/closer), ofertas, compras, attribution, LTV

```
```

## INTL — Intelligence & Platform

AI Copilot + Knowledge, Event Platform, Integrations, Observabilidade/indexação Elastic

```
```

## GWY — API Gateway

Spring Cloud Gateway — routing, auth, rate-limit

```
```

## REG — Service Registry

Eureka service discovery

```
```

## MIG — Migrations

Centralized Flyway DB migrations

```
```

## Total

**0 permissões canônicas** distribuídas em 10 módulos. O número cresce a cada novo recurso — atualizar o JSON (não este markdown).

## Validação automática

- O gerador (`scripts/be-module-generator.py`) valida ao scaffold que toda permissão referenciada em `@PreAuthorize` consta neste catálogo (D-060). Ops cujo verbo não mapeia para nenhuma ação canônica em `arch_decisions._OP_VERB_TO_ACTION` falham com erro explícito.
- `scripts/arch_decisions.py validate --aspect permission-catalogue` checa duplicatas, prefixos consistentes e `_schema_version`.
- `cross_validate_rbac_against_catalogue(rbac, catalogue)` checa que toda permissão listada em `roles[*].permission_bundle` (kind=`list`) consta no catálogo.

## Como adicionar permissão nova

1. Editar `templates/architecture/decisions/permission-catalogue.arch.json` — adicionar entrada em `modules[prefix=<modulo>].permissions`.
2. Bumpar `version` (semver) e `last_changed`.
3. Validar: `python scripts/arch_decisions.py validate`.
4. Re-renderizar este documento (`new-project` P2 ou comando equivalente).
5. Se o BE precisa permitir uso da permissão em algum papel, editar `rbac.arch.json` `roles[*].permission_bundle`.
6. Migração: adicionar `INSERT INTO journeyos_global.permissao` em `V<N>__iam_permissao_<codigo>.sql`.
7. Bumpar `journeyos_global.modelo_acesso_versao` para invalidar cache.

## Anti-patterns

- ❌ Editar este markdown direto — ele é gerado. Próximo render sobrescreve.
- ❌ Inventar permissão ad-hoc em código sem registrar no JSON — quebra auditoria + cache + validação do gerador.
- ❌ Permissão genérica `*` ou `<modulo>.*` no `papel_permissao` — sempre individual em runtime; wildcards só são aceitos na expansão de `permission_bundle` em tempo de geração.
- ❌ Esquecer de bumpar `journeyos_global.modelo_acesso_versao` após adicionar permissão — JWT antigo continua válido com modelo desatualizado.
- ❌ Renomear permissão depois de aplicada em produção — sempre criar nova + descontinuar antiga (depreciate em N versões).
