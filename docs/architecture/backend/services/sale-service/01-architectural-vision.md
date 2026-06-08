# 01 — Architectural Vision — SALE (Sales & Revenue)

> Camada de visão (Layer 1 — Architect). Gera contratos, não código.
> Módulo: **SALE** · serviço `sale-service` · pacote `com.journeyos.sale`.

## 1. Intent

SALE é o **motor de receita** do Journey OS. É dono da **venda** dentro de cada `empresa`:
organiza o **pipeline de CRM** (oportunidades movendo por estágios, atribuídas a SDR/closer),
o **catálogo de ofertas**, as **compras confirmadas** (receita reconhecida), a **atribuição de
receita** (de qual lead/jornada/campanha veio cada real) e o **LTV** por cliente. SALE transforma
um conjunto disperso de fechamentos (DM, call, checkout) em um **funil de receita rastreável,
explicável e auditável**, que alimenta INTL (analytics de receita), WRKS (auditoria) e fecha o
loop de growth ao revelar o ROI por origem.

## 2. Problem Statement

A persona Rafael (infoprodutor) fatura ~R$200k/mês, mas o faturamento vive espalhado entre Hotmart,
links de pagamento e planilhas de closer — **ninguém sabe dizer de onde veio cada venda**. Marina
(growth) não consegue provar o ROI de uma campanha porque a receita não está ligada à origem do lead.
Lucas (SDR/closer) trabalha oportunidades sem um pipeline único e perde o histórico de ganho/perda.

O Journey OS resolve isso com o SALE:

- **Pipeline único por empresa**: oportunidades vinculadas a leads, movendo por estágios configuráveis, com responsável e motivo de ganho/perda.
- **Ofertas versionadas**: catálogo de produto+preço que dá significado à receita.
- **Compra idempotente**: pedido confirmado registrado uma única vez por `id_externo` — receita nunca duplicada.
- **Atribuição explicável**: cada real atribuído a touchpoints (origem/jornada/campanha) por um modelo determinístico e versionado — não uma caixa-preta.
- **LTV rastreável**: valor vitalício por cliente, somando compras confirmadas com breakdown.

Sem SALE, cada relatório de faturamento reinventaria "quanto vendemos e por quê", gerando números
divergentes e nenhuma ligação confiável entre marketing e receita.

## 3. Personas

| Persona | Papel canônico | Relação com SALE |
|---|---|---|
| **Lucas — SDR / Closer** | `SDR` | Persona **principal**. Opera o pipeline: pega oportunidades, move estágios, registra ganho/perda. Vê apenas seu `data_scope`. |
| **Rafael — Infoprodutor / CEO** | `INFOPRODUTOR` | Persona **secundária**. Acompanha faturamento, LTV e saúde do funil de receita da empresa. |
| **Marina — Head de Growth** | `HEAD_GROWTH` | Persona **terciária**. Analisa atribuição/ROI por origem e campanha para realocar verba. |
| **Serviços do Journey OS** (LEAD, JRNY, COMM, INTL) | — (máquina) | LEAD emite `lead.qualificado` (cria/prioriza oportunidade); JRNY roteia; INTL indexa receita; COMM nutre. SALE não conhece seus consumidores diretamente. |

## 4. MVP Scope (in)

1. **Pipeline/CRM**: `oportunidade` (deal) vinculada a um lead, com `estagio` configurável, valor estimado, responsável (SDR/closer) e probabilidade; mover estágio; ganhar/perder com motivo.
2. **Ofertas**: catálogo de `oferta` (produto + preço + moeda + vigência), **versionado**.
3. **Compras**: ingestão **idempotente** de `compra` (pedido confirmado) por `id_externo`; `item_compra` (ofertas) + reconhecimento de receita.
4. **Atribuição de receita**: vincula a receita de uma compra aos touchpoints (origem do lead, jornada, campanha) por um **modelo determinístico e versionado** (default `last-touch`; `first-touch`/`linear` configuráveis).
5. **LTV**: valor vitalício por contato (soma de compras confirmadas + breakdown); recálculo em `compra.confirmada`.
6. **Consulta/funil**: oportunidades por estágio/responsável; receita por origem/campanha/período (apoio Elastic `revenue-events` / `campaign-events`).
7. **Eventos**: `oportunidade.criada`, `oportunidade.estagio.alterado`, `oportunidade.ganha`, `oportunidade.perdida`, `compra.confirmada`, `receita.atribuida`, `ltv.atualizado`.

## 5. Out of Scope (MVP)

- **Qualificação/scoring** de lead — responsabilidade de **LEAD** (SALE consome `lead.qualificado`).
- **Roteamento/atribuição** de SDR a lead — responsabilidade de **JRNY** (SALE consome a decisão).
- **Comunicação/cobrança/nutrição** — responsabilidade de **COMM**.
- **Processamento de pagamento** real (cobrar cartão, antifraude) — o gateway/checkout é externo; SALE registra a compra **já confirmada**.
- **Reconciliação financeira/contábil** completa (impostos, split, chargeback avançado) — MVP registra status básico.
- **Forecast de receita por ML** — previsão preditiva é pós-MVP.
- **Editor visual** de pipeline / modelo de atribuição — MVP via API/config.
- **Attribution data-driven** (probabilística/treinada) — MVP usa modelos determinísticos (last/first/linear-touch).

## 6. Architectural Principles

1. **Receita rastreável, nunca caixa-preta** — toda compra confirmada tem origem e toda atribuição registra o `modelo_atribuicao` + os touchpoints que a produziram (ver `ADR-005`).
2. **Idempotência da receita** — registrar o mesmo pedido (`id_externo` + `origem`) duas vezes resulta em **uma** compra; receita nunca é contada em dobro (ver `ADR-005`).
3. **SALE registra, não cobra** — o pagamento é executado por sistema externo; SALE é fonte da verdade da venda *reconhecida*, não do processamento financeiro.
4. **Hexagonal estrito** — domínio sem Spring/JPA; portas in/out; ArchUnit bloqueante (ver `ADR-001`).
5. **Isolamento por schema** — SALE escreve apenas no `emp_<slug>` resolvido por `EmpresaContextHolder`; nenhum dado vaza cross-empresa (ver `ADR-004`).
6. **Privacidade por design (LGPD)** — `compra` carrega base legal/consentimento do comprador; suporte a anonimização e expurgo.
7. **Eventos como contrato a jusante** — INTL/WRKS/COMM reagem a eventos `oportunidade.*`/`compra.*`/`receita.*`/`ltv.*`; SALE não conhece seus consumidores (ver `ADR-003`).

## 7. Success Signals

- Registrar a mesma compra (mesmo `id_externo`) duas vezes resulta em **uma** venda e **um** reconhecimento de receita (idempotência).
- Rafael abre o painel de receita e vê **quanto** faturou e **de qual origem/campanha** veio (atribuição), não só o total.
- Marina compara o ROI de duas campanhas porque a receita está ligada à origem do lead que comprou.
- Uma `compra.confirmada` dispara automaticamente a **atribuição de receita** e o recálculo de **LTV** de forma rastreável (modelo de atribuição registrado).
- Um lead que vira `lead.qualificado` aparece como **oportunidade** no pipeline do closer correto.
- Nenhuma consulta com JWT da empresa A retorna venda/receita da empresa B (cross-empresa guard).
- 100% das cláusulas SHALL das specs viram cenário BDD (gate D-218).

---

## Referências

- ADRs: `adr/ADR-001..005`
- Brief: `_brief.md`
- Blueprint: `02-architecture-blueprint.md`
- Multi-tenancy global: `docs/architecture/shared/multi-empresa.md`
- LEAD (dependência a montante): `docs/architecture/backend/services/lead-service/`
- WRKS (dependência): `docs/architecture/backend/services/wrks-service/`
