# ADR-005 — Maturity Score (6D): determinístico, explicável, assist IA opcional

**Status:** proposed

## Contexto

O coração do LEAD é o **Maturity Score** — um índice que diz *quão pronto para comprar* um lead
está. Para ser útil a Marina (calibrar) e Lucas (priorizar com confiança), o score precisa ser
**explicável** e **estável**. O Journey OS delega IA à **TechLab AI** (capacidade `qualification`),
mas a indisponibilidade dela não pode parar a qualificação. É a decisão crítica do domínio.

## Decisão

1. **6 dimensões** (proposta a confirmar nas specs): `PERFIL` (fit/ICP), `ENGAJAMENTO`, `INTENCAO`,
   `CAPACIDADE` (orçamento/poder de decisão), `URGENCIA` (timing), `ADERENCIA` (aderência ao conteúdo).
   O score agregado [0..100] é função das contribuições por dimensão.
2. **Determinístico e versionado**: o cálculo usa `regra_qualificacao` **versionada**. Toda
   `maturity_score` registra `versao_regra` + `hash_sinais`. Mesma entrada (lead + versão + sinais)
   → mesmo score (**idempotência**: chave = `lead_id` + `versao_regra` + `hash_sinais`).
3. **Explicável**: persiste o **breakdown** (`score_dimensao` + contribuintes) — nunca só o número.
4. **Assist IA opcional**: a TechLab AI (`qualification`) interpreta texto livre (surveys/notas) e
   **sugere** contribuições por dimensão; tais contribuições são marcadas com `origem=assist_ia` e
   **nunca** são a única fonte de uma transição de estado. Em falha/timeout (Resilience4j circuit
   breaker), o score é produzido só com as regras (fallback), com `assist_ia=false` no breakdown.
5. **Transições** `QUALIFICADO`/`NAO_QUALIFICADO` derivam exclusivamente do score vs. limiar configurável.

## Alternativas consideradas

- **Score por modelo de ML treinado por tenant**: maior potencial preditivo, mas opaco (sem
  breakdown), exige dados/treino e operação de MLOps. Rejeitada no MVP (mantida como evolução).
- **Score 100% via TechLab AI**: simples, mas cria dependência dura, não-determinística e pouco
  explicável; viola "score explicável, nunca caixa-preta". Rejeitada.
- **Score 1D (lead score único)**: insuficiente para Marina diagnosticar *por que* um lead está
  pronto. Rejeitada em favor das 6 dimensões.

## Consequências

**Positivas:** priorização confiável e auditável; calibração por config (sem deploy); resiliência a
falha de IA; trilha de auditoria via `versao_regra`.

**Negativas:** manter regras versionadas e o recálculo coerente exige disciplina; calibração inicial
das dimensões é incerta (ver R1/A1 em `06-risks-gaps-assumptions.md`). Por isso esta ADR está
**proposed** até a validação nas specs (SPEC-03) e o sync da TechLab AI (P3).

## Referências

- `03-initial-domain-framing.md` (invariantes 2–4) · `01-architectural-vision.md` (princípios 1–2,5)
- `docs/architecture/integrations/techlab-ai-integration.md` (capacidade `qualification`)
- ADR-001 (domain service puro) · ADR-003 (eventos de score)
