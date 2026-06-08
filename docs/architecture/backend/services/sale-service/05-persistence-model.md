# 05 — Persistence Model — SALE (Sales & Revenue)

> Estratégia de schema e rascunho de entidades. Detalhe em `/be-architect-specs` → `contracts/data-model.md` + SPEC-04.

## 1. Schema Strategy

- **Schema-per-tenant**: todos os dados operacionais do SALE vivem no schema `emp_<slug>` da empresa.
  SALE **não** escreve em `journeyos_global` (exclusivo de WRKS/MIG).
- O schema é provisionado por **MIG** (migrations centralizadas); SALE roda com
  `spring.jpa.hibernate.ddl-auto=validate` e `spring.jpa.open-in-view=false` (RULE-08).
- `EmpresaContextHolder` resolve o schema corrente a partir do JWT em cada requisição/consumo de evento.

## 2. Initial Entities (rascunho)

Identificadores em **pt-BR canônico**; chaves `UUID`; valores monetários em `NUMERIC(15,2)` + `moeda`.
Tabelas no schema `emp_<slug>` (sem coluna `empresa_id` — o schema isola o tenant).

| Tabela | Conteúdo | Notas |
|---|---|---|
| `oportunidade` | Agregado raiz CRM: `id`, `lead_id`, `estagio`, `valor_estimado`, `probabilidade`, `responsavel_id`, `estado`, `motivo_perda`, `criado_em`, `atualizado_em` | índice por `estagio`, `responsavel_id` |
| `historico_estagio` | `oportunidade_id`, `de_estagio`, `para_estagio`, `ator_id`, `ocorrido_em` | trilha do funil |
| `oferta` | Catálogo: `id`, `nome`, `sku`, `preco`, `moeda`, `versao`, `ativo`, `vigente_de`, `vigente_ate` | versionada |
| `compra` | Agregado raiz receita: `id`, `id_externo`, `origem`, `contato_ref`, `oportunidade_id`, `valor_total`, `moeda`, `status`, `base_legal`, `confirmada_em` | UNIQUE(`id_externo`,`origem`) por schema (idempotência) |
| `item_compra` | `compra_id`, `oferta_id`, `quantidade`, `valor_unitario`, `valor_total` | soma = `compra.valor_total` |
| `modelo_atribuicao` | `id`, `tipo` (last/first/linear), `versao`, `ativo`, `vigente_de` | config versionada (auditoria de atribuição) |
| `atribuicao` | `compra_id`, `touchpoint`, `tipo_touchpoint`, `valor_atribuido`, `versao_modelo`, `calculado_em` | breakdown; Σ `valor_atribuido` = `compra.valor_total` |
| `campanha` | `id`, `nome`, `origem`, `ativo`, `iniciada_em`, `encerrada_em` | alvo de atribuição (índice `campaign-events`) |
| `ltv` | `contato_ref`, `valor_total`, `num_compras`, `primeira_compra_em`, `ultima_compra_em`, `atualizado_em` | materializado; determinístico por compras |

Índices-chave: `compra(id_externo, origem)` UNIQUE; `oportunidade(estagio)`; `oportunidade(responsavel_id)`;
`atribuicao(compra_id)`; `ltv(contato_ref)`. Espelho de leitura/analytics no Elastic (`revenue-events`, `campaign-events`).

## 3. Migration Strategy

- **Flyway centralizado** em `journey-os-migrations` (MIG). Migrations do SALE nomeadas
  `V<N>__sale_<descricao>.sql`, schema-aware (aplicadas ao template `emp_<slug>`).
- SALE **não** roda Flyway próprio; valida o schema no boot.
- Seed de pipeline/estágios default, ofertas iniciais e `modelo_atribuicao` default (`last-touch`)
  por tenant é disparado pelo consumo de `journey-os.empresa.provisionada` (não por migration de dados global).

## 4. Data Lifecycle

- **LGPD**: `compra` carrega `base_legal` + dados do comprador (`contato_ref` + PII). Suporte a:
  - **Anonimização** (compras de contatos que exerceram direito ao esquecimento): remove PII, **preserva** valores agregados de receita/LTV para integridade financeira e estatística.
  - **Expurgo**: remoção física sob solicitação, com trilha em auditoria — exceto registros sob obrigação legal de retenção fiscal (configurável por empresa).
- **Imutabilidade da receita**: `compra` confirmada não é editada; ajustes ocorrem por novo estado (`ESTORNADA`/`CANCELADA`) que registra o delta — o histórico de receita é append-only para auditoria.
- **Retenção**: oportunidades `PERDIDA`/`DESCARTADA` sem atividade por período configurável → candidatas a arquivamento (política por empresa). MVP: marca; pipeline de retenção é pós-MVP.
- **Auditoria**: confirmação/estorno de compra e mudanças de estágio emitem eventos `compra.*`/`oportunidade.*` → WRKS consolida em `evento_auditoria`.
- **Histórico de receita/LTV**: a base transacional mantém o estado atual (LTV materializado, último modelo); a **série temporal completa** de receita é responsabilidade de INTL (Elastic `revenue-events`), não da base operacional.

---

## Referências

- `03-initial-domain-framing.md` (agregados/invariantes)
- `ADR-004` (multi-tenancy) · `ADR-005` (atribuição de receita / idempotência)
- `docs/architecture/shared/modelo-dados/{empresa,relacionamentos}.md`
- Detalhe DDL: `/be-architect-specs SALE` → `contracts/data-model.md` + `SPEC-04-data-model-migrations.md`
