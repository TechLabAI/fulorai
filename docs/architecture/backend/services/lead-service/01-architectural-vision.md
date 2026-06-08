# 01 — Architectural Vision — LEAD (Lead Intelligence & Qualification)

> Camada de visão (Layer 1 — Architect). Gera contratos, não código.
> Módulo: **LEAD** · serviço `lead-service` · pacote `com.journeyos.lead`.

## 1. Intent

LEAD é a **inteligência de leads** do Journey OS. É dono do **lead** dentro de cada `empresa`:
consolida o perfil a partir de múltiplas fontes, aplica regras de qualificação determinísticas
e calcula o **Maturity Score (6D)** — um índice multidimensional e *explicável* de prontidão de
compra. LEAD transforma uma base bruta e fragmentada de contatos em uma **fila priorizada,
auditável e roteável**, que alimenta JRNY (roteamento), SALE (pipeline) e COMM (nutrição).

## 2. Problem Statement

A persona Rafael (infoprodutor) captura leads em vários canais — Meta Ads, Hotmart, formulários,
landing pages, listas importadas — e termina com **a mesma pessoa repetida em planilhas diferentes**
e **sem nenhum critério único de prioridade**. Marina (growth) não consegue dizer com confiança
"esses 200 leads estão prontos e esses 5.000 não"; Lucas (SDR) recebe uma fila sem ordem e gasta
tempo com quem não vai comprar.

O Journey OS resolve isso com o LEAD:

- **Lead único por empresa**: ingestão idempotente + dedup por chave natural (email/telefone+fonte).
- **Perfil tipado**: atributos com origem e base legal (LGPD), enriquecidos por surveys.
- **Qualificação explicável**: regras versionadas mapeiam sinais → contribuição por dimensão.
- **Maturity Score (6D)**: um número agregado *com breakdown* — não uma caixa-preta — para priorizar.
- **Segmentação dinâmica**: predicados sobre perfil+score que reagrupam a base automaticamente.

Sem LEAD, cada módulo a jusante (JRNY, SALE, COMM) reinventaria "quem é esse lead e quanto vale",
gerando critérios divergentes e priorização inconsistente.

## 3. Personas

| Persona | Papel canônico | Relação com LEAD |
|---|---|---|
| **Marina — Head de Growth** | `HEAD_GROWTH` | Persona **principal**. Desenha regras de qualificação e segmentos; monitora a distribuição do Maturity Score e a saúde da base; ajusta pesos por dimensão. |
| **Lucas — SDR / Closer** | `SDR` | Persona **secundária**. Consome a fila priorizada de leads qualificados; precisa do *porquê* (breakdown do score) para abordar bem. Vê apenas seu `data_scope`. |
| **Rafael — Infoprodutor / CEO** | `INFOPRODUTOR` | Persona **terciária**. Visão consolidada da qualidade e do volume qualificado da base. |
| **Serviços do Journey OS** (JRNY, SALE, COMM, INTL) | — (máquina) | Consomem `lead.qualificado` / `lead.score.atualizado` para rotear, priorizar, nutrir e indexar. |

## 4. MVP Scope (in)

1. **Lead capture**: ingestão idempotente (`POST /api/v1/leads`) por `chave_natural`; dedup/merge exato e normalizado; registro de fonte e base legal (LGPD).
2. **Perfil**: `lead` + `perfil_lead` (atributos tipados com origem); consentimento e ciclo de vida do dado.
3. **Surveys**: `survey` + `pergunta` + `resposta_survey`; respostas atualizam o perfil e disparam recálculo de score.
4. **Qualification rules**: `regra_qualificacao` config-driven e **versionada**; mapeia sinais → contribuição por dimensão.
5. **Maturity Score (6D)**: cálculo determinístico das 6 dimensões + agregado + **breakdown explicável**; **assist opcional da TechLab AI** (`qualification`) com fallback determinístico.
6. **Segmentação**: `segmento` dinâmico (predicado sobre perfil+score); reavaliação ao mudar perfil/score; emissão de `lead.segmento.alterado`.
7. **Fila/consulta**: listagem priorizada por score com filtros por segmento/dimensão (apoio Elastic índice `leads`).
8. **Eventos**: `lead.capturado`, `lead.qualificado`, `lead.score.atualizado`, `lead.segmento.alterado`.

## 5. Out of Scope (MVP)

- **Roteamento/atribuição** de lead a SDR/jornada — responsabilidade de **JRNY**.
- **Pipeline/oportunidade/venda** — responsabilidade de **SALE**.
- **Disparo de comunicação/nutrição** — responsabilidade de **COMM**.
- Deduplicação **probabilística** (ML/fuzzy) — MVP usa chave natural + match normalizado.
- Enriquecimento via provedores externos pagos (Clearbit, Serasa, etc.).
- Scoring **preditivo treinado por tenant** — MVP usa regras versionadas + assist TechLab AI estável.
- Editor **visual** de regras/segmentos — MVP via API/config.
- Importação em massa com pipeline assíncrono dedicado — MVP: ingestão unitária + lote pequeno síncrono.

## 6. Architectural Principles

1. **Score explicável, nunca caixa-preta** — todo Maturity Score tem breakdown por dimensão e referência à versão de regra que o produziu (ver `ADR-005`).
2. **Determinismo + idempotência** — recalcular o mesmo lead com as mesmas regras/sinais produz o mesmo resultado; a TechLab AI é *assist*, não fonte da verdade (ver `ADR-005`).
3. **Hexagonal estrito** — domínio sem Spring/JPA; portas in/out; ArchUnit bloqueante (ver `ADR-001`).
4. **Isolamento por schema** — LEAD escreve apenas no `emp_<slug>` resolvido por `EmpresaContextHolder`; nenhum dado vaza cross-empresa (ver `ADR-004`).
5. **IA via TechLab AI, com fallback** — nenhuma chamada direta a provedor de IA; falha de IA degrada para o resultado determinístico, nunca derruba a qualificação.
6. **Privacidade por design (LGPD)** — todo lead carrega base legal/consentimento; suporte a anonimização e expurgo.
7. **Eventos como contrato a jusante** — JRNY/SALE/COMM/INTL reagem a eventos `lead.*`; LEAD não conhece seus consumidores (ver `ADR-003`).

## 7. Success Signals

- Capturar o mesmo lead (mesma `chave_natural`) duas vezes resulta em **um** lead, não dois (idempotência/dedup).
- Um SDR abre um lead da fila e vê **por que** ele tem score alto (breakdown das 6 dimensões), não só o número.
- Mudar uma regra de qualificação recalcula os leads afetados e emite `lead.score.atualizado` de forma rastreável (versão de regra registrada).
- Indisponibilidade da TechLab AI **não** impede a qualificação — o score determinístico é produzido normalmente.
- Nenhuma consulta com JWT da empresa A retorna lead da empresa B (cross-empresa guard).
- Um lead que cruza o limiar de um segmento dispara `lead.segmento.alterado` e passa a aparecer na fila correspondente.
- 100% das cláusulas SHALL das specs viram cenário BDD (gate D-218).

---

## Referências

- ADRs: `adr/ADR-001..005`
- Brief: `_brief.md`
- Blueprint: `02-architecture-blueprint.md`
- Multi-tenancy global: `docs/architecture/shared/multi-empresa.md`
- TechLab AI: `docs/architecture/integrations/techlab-ai-integration.md`
- WRKS (dependência): `docs/architecture/backend/services/wrks-service/`
