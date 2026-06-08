# 06 — Risks, Gaps & Assumptions — SALE (Sales & Revenue)

> Tudo que pode invalidar a visão ou exige decisão antes/ao longo das specs.

## 1. Riscos

| # | Risco | Impacto | Mitigação |
|---|---|---|---|
| R1 | **Atribuição imprecisa** (touchpoints incompletos) distorce o ROI por origem/campanha | Alto | Modelo de atribuição determinístico, versionado e **explicável** (breakdown); default conservador (`last-touch`); enriquecimento de touchpoints (JRNY/COMM) marcado como evolução. |
| R2 | **Receita duplicada** por webhook/reprocesso do checkout | Alto | Idempotência forte por (`id_externo`+`origem`) com UNIQUE no schema; ingestão idempotente testada em BDD. |
| R3 | **Inconsistência financeira** (Σ itens ≠ total; Σ atribuição ≠ receita) | Alto | Invariantes 2 e 4 (`03`) validadas no domínio; testes de conservação de receita. |
| R4 | **PII de comprador vazando** em logs/eventos/Elastic (LGPD) | Alto | MDC sem PII; eventos carregam IDs/valores, não PII sensível; índices de receita com campos controlados; anonimização/expurgo suportados. |
| R5 | **Estorno/cancelamento** mal modelado corrompe LTV e relatórios | Médio | Estado explícito (`ESTORNADA`/`CANCELADA`) com delta rastreável; LTV recalculado de forma determinística; histórico append-only. |
| R6 | **Acoplamento a fontes de compra** (checkout/gateway) ainda indefinidas | Médio | Ingestão por API idempotente desacopla do gateway; Event Platform do INTL é o caminho pós-MVP; contrato de `compra` estável. |
| R7 | **Dependência de LEAD/JRNY** que podem não existir ainda | Baixo | Integração por eventos (consumidores opcionais); compra direta funciona sem oportunidade; oportunidade pode ser criada por API. |

## 2. Gaps Conhecidos

- **Conjunto final de estágios do pipeline** e regras de transição — proposta no brief, a confirmar em `/be-architect-specs` (SPEC sobre pipeline/CRM).
- **Modelos de atribuição suportados** e a semântica exata de `linear`/multi-touch — a especificar (default `last-touch` no MVP).
- **Contrato exato da `compra`** vindo do checkout/gateway (campos do `id_externo`, `origem`, itens) — depende da fonte (Hotmart/link) e do Event Platform do INTL (pós-MVP).
- **Schema dos índices Elastic `revenue-events` e `campaign-events`** — campos indexados e mapeamentos a especificar.
- **Política de retenção fiscal/arquivamento** por empresa — a detalhar (MVP só marca).
- **Definição de `contato_ref`** (chave do cliente para LTV) e sua relação com o `lead` de LEAD — a alinhar nas specs.

## 3. Suposições a Validar

| # | Suposição | Como validar |
|---|---|---|
| A1 | `last-touch` como default de atribuição atende o MVP | Revisão com growth (Marina) nas specs; ajustar modelos suportados. |
| A2 | Kafka/AWS MSK é o event bus (não Artemis) | Confirmado por `project-context.json` + precedente WRKS/LEAD; `ADR-003`. |
| A3 | SALE escreve apenas no `emp_<slug>` (nada no global) | Alinhado a WRKS/LEAD; ArchUnit/review. |
| A4 | SALE não processa pagamento — só registra compra confirmada | Confirmar a fronteira com a fonte de checkout (INTL Event Platform) nas specs. |
| A5 | `contato_ref` permite consolidar LTV mesmo sem oportunidade/lead vinculado | Definir chave de contato nas specs (email/documento normalizado). |
| A6 | Os índices `revenue-events`/`campaign-events` (fact) bastam para o funil/ROI sem store de leitura dedicado | Validar performance de consulta no piloto. |
| A7 | Ingestão de compra unitária + lote pequeno síncrono atende o volume do MVP | Estimar volume de pedidos por empresa no piloto. |

## 4. Dependências Críticas

- **WRKS** disponível (AccessDecision/JWT + eventos `empresa.provisionada` / `modelo.acesso.alterado`) — **bloqueante** para autorização e seed por tenant.
- **MIG** com schema `emp_<slug>` provisionado — **bloqueante** para boot (`ddl-auto=validate`).
- **LEAD** emitindo `lead.qualificado` / `lead.score.atualizado` — **não bloqueante** (oportunidade pode ser criada por API); habilita o golden path automático.
- **Fonte de compra** (checkout/gateway via API idempotente; INTL Event Platform pós-MVP) — **bloqueante** para o reconhecimento de receita automático.
- **REG (Eureka)** — para descoberta do `wrks-service` via Feign.
- **Kafka/AWS MSK** e **Elasticsearch** disponíveis no ambiente local/dev.
- **TechLab AI**: **não** é dependência no MVP (atribuição/LTV determinísticos).

---

## Referências

- `01-architectural-vision.md` (princípios) · `04-backend-architecture-direction.md` (integrações)
- ADRs: `adr/ADR-001..005`
- `docs/architecture/backend/services/lead-service/` (contrato dos eventos consumidos)
- CLAUDE.md (regra: SALE sem chamada direta a gateway de pagamento; integrações externas via INTL/Event Platform)
