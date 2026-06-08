# Papéis canônicos — sementes SQL

> Aplicado em V1 do `journey-os-migrations` (schema `journeyos_global`).
> Detalhes de cada papel: [`modelo.md`](modelo.md) §1.
>
> **Fonte de verdade:** `templates/architecture/decisions/rbac.arch.json` (D-058).
> Este markdown é gerado deterministicamente a partir daquele JSON.

## 3 papéis padrão (todas as empresas)

```sql
INSERT INTO journeyos_global.papel (papel_id, codigo, nome, descricao, ativo) VALUES
  (gen_random_uuid(), 'INFOPRODUTOR', 'Infoprodutor / CEO da operação', 'Rafael, infoprodutor de marketing digital, fatura ~R$200k/mês, opera com Hotmart + ActiveCampaign + Meta Ads + planilhas e uma equipe de 4-8 pessoas.', true),
  (gen_random_uuid(), 'HEAD_GROWTH', 'Head de Growth / Marketing', 'Marina, head de growth de uma operação de educação que gerencia aquisição, nutrição e a equipe de tráfego/copy.', true),
  (gen_random_uuid(), 'SDR', 'SDR / Closer', 'Lucas, SDR que recebe filas de leads qualificados e precisa saber quem priorizar.', true);
```

## Bundles de permissões por papel

Os bundles são definidos via `papel_permissao` e podem mudar conforme negócio. Configuração canônica recomendada:

### INFOPRODUTOR

TODO: refine permissions — defaulted to `all` because per-role authority is not declared in discovery. Edit before going to production.

```sql
INSERT INTO journeyos_global.papel_permissao (papel_id, permissao_id)
SELECT (SELECT papel_id FROM journeyos_global.papel WHERE codigo='INFOPRODUTOR'),
       permissao_id
FROM journeyos_global.permissao;
```

### HEAD_GROWTH

TODO: refine permissions — defaulted to `all` because per-role authority is not declared in discovery. Edit before going to production.

```sql
INSERT INTO journeyos_global.papel_permissao (papel_id, permissao_id)
SELECT (SELECT papel_id FROM journeyos_global.papel WHERE codigo='HEAD_GROWTH'),
       permissao_id
FROM journeyos_global.permissao;
```

### SDR

TODO: refine permissions — defaulted to `all` because per-role authority is not declared in discovery. Edit before going to production.

```sql
INSERT INTO journeyos_global.papel_permissao (papel_id, permissao_id)
SELECT (SELECT papel_id FROM journeyos_global.papel WHERE codigo='SDR'),
       permissao_id
FROM journeyos_global.permissao;
```

## Como adicionar papel novo

1. Editar `templates/architecture/decisions/rbac.arch.json` — adicionar entrada em `roles`.
2. Validar com `python scripts/arch_decisions.py validate --aspect rbac`.
3. Re-renderizar este documento (`new-project` P2 ou comando equivalente).
4. Bumpar `rbac.version` no JSON (semver) e `last_changed`.
5. Migração: adicionar `INSERT INTO journeyos_global.papel` em `V<N>__iam_papel_<codigo>.sql` espelhando a entrada nova.
6. Se afeta UI, atualizar `frontend/libs/iam/feature-permissoes/` para mostrar opção.
7. Bumpar `journeyos_global.modelo_acesso_versao` para invalidar cache.

## Anti-patterns

- ❌ Editar este markdown direto — ele é gerado. Próximo render sobrescreve.
- ❌ Criar papel ad-hoc por empresa — papéis são **canônicos do grupo**; o que muda é a *associação* `usuario_empresa`.
- ❌ Bundle de permissões "wildcard" tipo `*.*` — sempre listar explicitamente (auditoria precisa rastrear).
- ❌ Permitir que GERENTE acesse `iam.*` — escalação de privilégio.
