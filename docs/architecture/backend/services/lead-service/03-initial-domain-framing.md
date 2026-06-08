# 03 — Initial Domain Framing — LEAD (Lead Intelligence & Qualification)

> Rascunho de linguagem ubíqua, agregados e eventos. Refinado em `/be-architect-specs` (contracts/data-model).

## 1. Ubiquitous Language

| Termo (pt-BR) | Definição |
|---|---|
| **Lead** | Pessoa/contato capturado por uma `empresa`, candidato a se tornar comprador. Agregado raiz. |
| **Chave natural** | Identificador de deduplicação do lead (email e/ou telefone normalizado + fonte). |
| **Perfil do lead** (`perfil_lead`) | Conjunto de atributos tipados (origem, base legal) que descrevem o lead. |
| **Atributo de perfil** | Par chave→valor tipado com `origem` (form, survey, integração, assist IA) e timestamp. |
| **Survey** | Questionário versionado aplicado ao lead; suas respostas alimentam o perfil. |
| **Resposta de survey** (`resposta_survey`) | Resposta de um lead a uma `pergunta` de um `survey`. |
| **Regra de qualificação** (`regra_qualificacao`) | Definição versionada que mapeia sinais do perfil → contribuição por dimensão. |
| **Dimensão** | Um dos 6 eixos do Maturity Score: `PERFIL`, `ENGAJAMENTO`, `INTENCAO`, `CAPACIDADE`, `URGENCIA`, `ADERENCIA` *(a confirmar em specs)*. |
| **Maturity Score (6D)** | Índice agregado [0..100] derivado das 6 dimensões, com **breakdown** explicável e `versao_regra`. |
| **Breakdown** | Decomposição do score por dimensão + regras/sinais que contribuíram (explicabilidade). |
| **Assist IA** | Contribuição **sugerida** pela TechLab AI (`qualification`) sobre texto livre; opcional, marcada na origem. |
| **Segmento** | Grupo dinâmico definido por um predicado sobre perfil+score; um lead entra/sai automaticamente. |
| **Qualificação** | Estado do lead após o cálculo do score atingir/cruzar critérios (ex.: `NAO_QUALIFICADO` → `QUALIFICADO`). |

## 2. Aggregates and Entities (rascunho inicial)

- **Lead** (agregado raiz)
  - `Lead` (id, empresa_id implícito por schema, chave_natural, fonte, estado_qualificacao, base_legal, criado_em)
  - `PerfilLead` (1–1 com Lead) + `AtributoPerfil` (N) — atributos tipados com origem
  - `MaturityScore` (último score: valor agregado + `versao_regra` + hash_sinais + assist_ia + calculado_em)
  - `ScoreDimensao` (N: dimensão → valor + contribuintes) — o breakdown
- **Survey** (agregado)
  - `Survey` (id, nome, versao, ativo) + `Pergunta` (N, tipada)
  - `RespostaSurvey` (vincula lead ↔ pergunta) — pertence ao contexto do lead
- **RegraQualificacao** (agregado de configuração, versionado)
  - `RegraQualificacao` (id, versao, ativo, vigente_de) + `CondicaoRegra` (N: sinal → dimensão → peso)
- **Segmento** (agregado de configuração)
  - `Segmento` (id, nome, predicado, ativo) — avaliação dinâmica; associação lead↔segmento materializada

## 3. Domain Events (inicial)

**Produzidos** (Kafka / AWS MSK):

| Evento | Quando | Principais consumidores |
|---|---|---|
| `journey-os.lead.capturado` | Lead criado/atualizado na ingestão | INTL (analytics), WRKS (auditoria) |
| `journey-os.lead.qualificado` | Maturity Score calculado e lead atinge estado qualificado (**âncora**) | JRNY (roteamento), SALE (priorização), COMM (nutrição) |
| `journey-os.lead.score.atualizado` | Recálculo de score (survey, mudança de regra, novo sinal) | JRNY, SALE, INTL |
| `journey-os.lead.segmento.alterado` | Lead entra/sai de um segmento | COMM (nutrição segmentada), JRNY |

**Consumidos:**

| Evento | Origem | Reação |
|---|---|---|
| `journey-os.empresa.provisionada` | WRKS | Seed de regras/segmentos default no novo `emp_<slug>` |
| `journey-os.modelo.acesso.alterado` | WRKS | Invalida cache de `AccessDecision` |

*(Pós-MVP: consumir sinais de engajamento de COMM/JRNY para alimentar a dimensão `ENGAJAMENTO`.)*

## 4. State Transitions (alto nível)

**Estado de qualificação do Lead:**

```
NOVO ──(perfil mínimo)──▶ EM_QUALIFICACAO ──(score ≥ limiar)──▶ QUALIFICADO
  │                                │                                  │
  │                                ├──(score < limiar)──▶ NAO_QUALIFICADO
  │                                                                   │
  └────────────────────── DESCARTADO / ANONIMIZADO (LGPD) ◀───────────┘
```

- Transições para `QUALIFICADO`/`NAO_QUALIFICADO` são sempre **resultado do cálculo do score** (determinístico).
- `ANONIMIZADO` é terminal (LGPD): mantém o agregado para integridade referencial, sem PII.

## 5. Invariants

1. Um lead é **único por `empresa` + `chave_natural`** (dedup garante não duplicação).
2. Todo `MaturityScore` referencia uma `versao_regra` existente e carrega o `hash_sinais` que o produziu (idempotência/auditoria).
3. O score agregado é função **determinística** das contribuições por dimensão; a mesma entrada produz o mesmo score.
4. Contribuição de **assist IA** é sempre marcada como tal na origem e **nunca** é a única fonte de uma transição de estado.
5. Todo lead tem `base_legal` definida antes de qualquer processamento de qualificação (LGPD).
6. Um lead só pertence a um `segmento` se o predicado do segmento for verdadeiro para seu perfil+score no momento da avaliação.
7. Toda escrita ocorre no schema `emp_<slug>` do contexto corrente — nunca cross-empresa.

---

## Referências

- `02-architecture-blueprint.md` · `05-persistence-model.md`
- ADR-005 (Maturity Score 6D) · ADR-003 (messaging) · ADR-004 (multi-tenancy)
- Specs detalhados: `/be-architect-specs LEAD` → `contracts/data-model.md`, `events/event-catalog.md`
