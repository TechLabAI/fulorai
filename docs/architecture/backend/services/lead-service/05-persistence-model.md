# 05 — Persistence Model — LEAD (Lead Intelligence & Qualification)

> Estratégia de schema e rascunho de entidades. Detalhe em `/be-architect-specs` → `contracts/data-model.md` + SPEC-04.

## 1. Schema Strategy

- **Schema-per-tenant**: todos os dados operacionais do LEAD vivem no schema `emp_<slug>` da empresa.
  LEAD **não** escreve em `journeyos_global` (exclusivo de WRKS/MIG).
- O schema é provisionado por **MIG** (migrations centralizadas); LEAD roda com
  `spring.jpa.hibernate.ddl-auto=validate` e `spring.jpa.open-in-view=false` (RULE-08).
- `EmpresaContextHolder` resolve o schema corrente a partir do JWT em cada requisição/consumo de evento.
- **pgvector** disponível no schema (embeddings de perfil para similaridade são **pós-MVP**).

## 2. Initial Entities (rascunho)

Identificadores em **pt-BR canônico**; chaves `UUID`. Tabelas no schema `emp_<slug>`.

| Tabela | Conteúdo | Notas |
|---|---|---|
| `lead` | Agregado raiz: `id`, `chave_natural`, `fonte`, `estado_qualificacao`, `base_legal`, `consentimento_em`, `criado_em`, `atualizado_em` | UNIQUE(`chave_natural`) por schema (dedup) |
| `perfil_lead` | 1–1 com `lead`: dados consolidados | — |
| `atributo_perfil` | N atributos tipados: `lead_id`, `chave`, `valor`, `tipo`, `origem`, `registrado_em` | origem ∈ {form, survey, integracao, assist_ia} |
| `survey` | `id`, `nome`, `versao`, `ativo` | versionado |
| `pergunta` | `survey_id`, `ordem`, `enunciado`, `tipo`, `dimensao_alvo` | mapeia para dimensão do score |
| `resposta_survey` | `lead_id`, `pergunta_id`, `valor`, `respondido_em` | alimenta `atributo_perfil` |
| `regra_qualificacao` | `id`, `versao`, `ativo`, `vigente_de` | versionada (auditoria de score) |
| `condicao_regra` | `regra_id`, `sinal`, `operador`, `valor_ref`, `dimensao`, `peso` | sinal → contribuição |
| `maturity_score` | `lead_id`, `valor_agregado`, `versao_regra`, `hash_sinais`, `assist_ia`, `calculado_em` | último score; idempotência por (`lead_id`,`versao_regra`,`hash_sinais`) |
| `score_dimensao` | `maturity_score_id`, `dimensao`, `valor`, `contribuintes` (jsonb) | breakdown explicável |
| `segmento` | `id`, `nome`, `predicado`, `ativo` | grupo dinâmico |
| `lead_segmento` | `lead_id`, `segmento_id`, `entrou_em` | associação materializada |

Índices-chave: `lead(chave_natural)` UNIQUE; `lead(estado_qualificacao)`; `maturity_score(lead_id)`;
`lead_segmento(segmento_id)`. Espelho de leitura/analytics no Elastic (`leads`).

## 3. Migration Strategy

- **Flyway centralizado** em `journey-os-migrations` (MIG). Migrations do LEAD nomeadas
  `V<N>__lead_<descricao>.sql`, schema-aware (aplicadas ao template `emp_<slug>`).
- LEAD **não** roda Flyway próprio; valida o schema no boot.
- Seed de `regra_qualificacao` e `segmento` default por tenant é disparado pelo consumo de
  `journey-os.empresa.provisionada` (não por migration de dados global).

## 4. Data Lifecycle

- **LGPD**: `lead` carrega `base_legal` + `consentimento_em`. Suporte a:
  - **Anonimização** (estado terminal `ANONIMIZADO`): remove PII de `lead`/`perfil_lead`/`atributo_perfil`, preserva agregados de score para integridade/estatística.
  - **Expurgo** (direito ao esquecimento): remoção física sob solicitação, com trilha em auditoria.
- **Retenção**: leads `DESCARTADO`/`NAO_QUALIFICADO` sem atividade por período configurável → candidatos a arquivamento (política por empresa). MVP: marca para expurgo; pipeline de retenção é pós-MVP.
- **Auditoria**: mudanças de estado e recálculos emitem eventos `lead.*` → WRKS consolida em `evento_auditoria`.
- **Histórico de score**: `maturity_score` mantém o último; histórico completo (série temporal) é responsabilidade de INTL (Elastic/analytics), não da base transacional.

---

## Referências

- `03-initial-domain-framing.md` (agregados/invariantes)
- `ADR-004` (multi-tenancy) · `ADR-005` (Maturity Score / idempotência)
- `docs/architecture/shared/modelo-dados/{empresa,relacionamentos}.md`
- Detalhe DDL: `/be-architect-specs LEAD` → `contracts/data-model.md` + `SPEC-04-data-model-migrations.md`
