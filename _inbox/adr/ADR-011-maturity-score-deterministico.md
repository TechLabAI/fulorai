# ADR-011 — Maturity Score calculado por lógica determinística (IA recomenda, não substitui o cálculo)

> **Data:** 2026-06-04
> **Status:** draft (BA)
> **Decisor:** Arquiteto (Danilo Amaral) — pendente de promoção

---

## Contexto

O Maturity Score multidimensional (6 dimensões: ICP, Awareness, Financial,
Implementation, Engagement, Moment) é diferencial competitivo do Journey OS frente
a scoring por tag/lista de RD/GoHighLevel (LBC §5.1, §11). O score posiciona o
lead na jornada, alimenta o Routing Engine (ADR-009) e é exibido para o SDR
(Persona 3, LBC §4.4). O QualificationEngine (Framing §6.4) calcula esses scores.

A decisão técnica: **como calcular o Maturity Score** — por lógica determinística
(regras/fórmulas versionadas) ou por modelo de IA/ML generativa? O princípio é
análogo ao do BOSQ ("cálculo determinístico antes de IA") e ao princípio de
segurança operacional do Journey OS: a IA recomenda/explica sobre o calculado,
mas não decide silenciosamente (LBC §8.4; Framing §2.4).

---

## Opções consideradas

### Opção A — Score determinístico (regras/fórmulas versionadas) (DECIDIDA)
- **Vantagens:**
  - Reproduzível e auditável: mesmo input → mesmo score; explica-se "o que puxou
    a dimensão Financial para cima/baixo" (wireframe — aba AI do Asset/Lead cita
    fonte do score).
  - Não exige dados rotulados (inexistentes com 1 cliente piloto).
  - Consistente entre workspaces (multi-tenant) e versionável (auditar mudança de
    fórmula).
  - Casa com o princípio de explicabilidade do routing (ADR-009).
- **Desvantagens:**
  - Calibrar os pesos das 6 dimensões exige conhecimento de domínio e iteração.
  - Não "aprende" sozinho com o tempo (requer ajuste manual das regras).
- **Custo:** médio (modelagem das regras).

### Opção B — Score por IA/ML generativa
- **Vantagens:**
  - Poderia capturar sinais sutis; "aprenderia" com dados.
- **Desvantagens:**
  - Black-box: não explica por que o score é X — fere o diferencial de
    explicabilidade e a segurança operacional (LBC §8.4).
  - Exige volume de dados históricos rotulados que o MVP/piloto não tem.
  - Não reproduzível (variabilidade do LLM) — péssimo para um score que decide
    routing comercial.
- **Custo:** alto; prematuro e contra o princípio.

### Opção C — Híbrido: base determinística + ajuste por IA no score final
- **Vantagens:**
  - Combina reprodutibilidade com adaptação.
- **Desvantagens:**
  - Se a IA altera o número final, perde-se a reprodutibilidade/auditoria do
    cálculo; difícil explicar o score resultante.
  - Complexidade sem dados para justificar no MVP.
- **Custo:** alto; prematuro.

---

## Decisão

Escolhida: **Opção A — Maturity Score determinístico**. A IA (ADR-002)
**recomenda sobre o calculado** (ex.: "leads com Financial baixo: ofereça
parcelamento", "este asset costuma elevar Engagement") e **explica** o score, mas
**não recalcula nem substitui** o número — o cálculo permanece determinístico e
auditável.

---

## Justificativa

1. **O diferencial é o score multidimensional explicável, não um número opaco
   (LBC §5.1/§11).** Um score que o SDR não entende não gera confiança (Persona
   3). Determinístico permite "por que este lead está Decision Ready".

2. **Sem dados para ML, e ML feriria a auditoria.** Com 1 cliente piloto não há
   histórico rotulado; e mesmo havendo, um score que decide routing comercial
   (ADR-009) precisa ser reproduzível e auditável (LBC §8.4) — ML black-box não é.

3. **Coerência com o princípio "IA recomenda, não decide" (§2.4).** A IA agrega
   valor na camada de recomendação/explicação sobre o cálculo, mantendo o humano
   e a auditoria no controle do número.

---

## Trade-offs aceitos

- **Perdemos:** a adaptação automática do ML. Justificativa: sem dados e contra a
  auditabilidade no MVP; a IA recomenda sobre o calculado e regras podem ser
  recalibradas/versionadas.
- **Perdemos:** captura de sinais sutis que só modelo aprenderia. Justificativa:
  reprodutibilidade e explicabilidade valem mais para um score que move decisão
  comercial; ML preditivo pode ser reavaliado em V3 (LBC §7.3) como sugestão,
  nunca substituindo o cálculo auditável.

---

## Como reverter se a decisão se mostrar errada

**Recalibrar as fórmulas:** versionar novas regras de score — barato, sem mudar
arquitetura. **Custo:** baixo, contínuo.

**Introduzir ML como recomendador (evolução, não reversão):** o ML sugere ajuste
de pesos ou sinaliza leads, ainda exibido como **recomendação** ao lado do score
determinístico, que permanece a fonte do número. **Custo:** incremental, V3.

Substituir o cálculo por ML black-box **não é reversão aceitável**: removeria a
explicabilidade que é o diferencial — só com pivô de produto.

---

## Sinais que indicariam que está errada

- Score determinístico divergindo sistematicamente da conversão real (leads de
  score alto não convertem; baixo converte) mesmo após recalibração — sinal de que
  as dimensões/pesos estão errados (recalibrar, não trocar o paradigma).
- SDRs/infoprodutor não confiando no score por não entendê-lo — falha de
  explicabilidade, não do determinismo.
- Volume e qualidade de dados suficientes surgindo (pós-PMF) que justifiquem ML
  **como recomendador** — gatilho de V3, não reversão.

---

## Consequências

- **Em código:** `QualificationEngine` (Framing §6.4) com score engine
  determinístico versionado (6 dimensões + final); domínio puro testável
  (ADR-004); `LeadScored`/`LeadQualified` como eventos (ADR-008).
- **Em IA:** advisors recomendam/explicam sobre o score (ADR-002), citando fonte.
- **Em produto:** score e sua explicação expostos na UI (wireframe — Lead detail,
  aba AI).

---

## Referências

- LBC §5.1 (Maturity 6D como valor), §8 (IA gera valor / §8.4 segurança operacional),
  §11 (diferencial vs scoring por tag), §4.4 (SDR precisa entender o score)
- Framing §2.4 (IA com evidência, recomenda), §3.1/§6.4 (QualificationEngine, 6 dimensões), §7.2 (LeadScore)
- Constraints: TECH-005 (IA via TechLab AI / event-first)
- ADRs relacionados: ADR-009 (routing usa o score; mesmo princípio determinístico+explicável),
  ADR-002 (IA recomenda sobre o calculado), ADR-008 (eventos de score)
