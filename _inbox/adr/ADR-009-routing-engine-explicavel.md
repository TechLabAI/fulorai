# ADR-009 — Routing Engine com regras versionadas e decision log (explicabilidade)

> **Data:** 2026-06-04
> **Status:** draft (BA)
> **Decisor:** Arquiteto (Danilo Amaral) — pendente de promoção

---

## Contexto

A proposta de valor central do Journey OS é mudar a pergunta operacional de
"qual automação executar?" para **"qual é a melhor próxima ação para este
lead?"** (LBC §1, §5). O Routing Engine decide o próximo passo do lead a partir
de 4 contextos (perfil, jornada, comportamento, receita) e **registra a
decisão** — regra disparada, condições avaliadas, ação (Framing §2.5/§8.2). A
explicabilidade é diferencial competitivo explícito frente a RD/Hotmart/
GoHighLevel (LBC §11): o SDR/closer precisa saber **por que** o lead foi roteado
para ele (Persona 3, LBC §4.4).

A decisão técnica: **como implementar o motor de decisão de próxima ação** de
forma que seja explicável, auditável e que combata o modelo legado de
"Tag → Automação" que o produto critica (LBC §3.2).

---

## Opções consideradas

### Opção A — Regras declarativas versionadas + decision log (DECIDIDA)
- **Vantagens:**
  - Cada decisão registra regra disparada, condições avaliadas e ação →
    explicabilidade nativa (Framing §2.5); cumpre o diferencial do produto.
  - Regras versionadas permitem auditar "qual versão da política decidiu isto".
  - Hierarquia de prioridades determinística → mesmo input, mesma decisão
    (testável e reproduzível).
  - Decision log projetado para `routing-decisions-*` (Elastic, ADR-007) para
    análise/observabilidade.
- **Desvantagens:**
  - Exige um editor/runtime de regras (RuleEditor no Automation Builder — wireframe
    TELA 10) e disciplina de modelagem das condições.
  - Regras podem proliferar e ficar difíceis de manter sem governança.
- **Custo:** médio.

### Opção B — Automação por tag/gatilho (modelo legado "Tag → Automação")
- **Vantagens:**
  - Simples, familiar ao mercado (RD/ActiveCampaign); rápido de entregar.
- **Desvantagens:**
  - É exatamente o modelo que o Journey OS **combate** (LBC §3.2): não lê contexto
    multidimensional (perfil/jornada/comportamento/receita) e não explica a
    decisão. Adotá-lo destruiria o diferencial.
- **Custo:** baixo, mas anula a proposta de valor.

### Opção C — Modelo de ML para próxima ação (black-box)
- **Vantagens:**
  - Pode capturar padrões sutis; "aprende" com dados.
- **Desvantagens:**
  - Black-box: não explica **por que** roteou (viola §2.5 e o princípio "IA
    recomenda sobre o calculado, não substitui o determinístico", ADR-011).
  - Exige volume de dados rotulados inexistente no MVP/piloto (1 cliente).
  - Decisão não auditável fere a confiança do SDR e o princípio de segurança
    operacional (LBC §8.4).
- **Custo:** alto, prematuro e contra o princípio de explicabilidade.

---

## Decisão

Escolhida: **Opção A — regras declarativas versionadas + decision log**. A IA
(ADR-002) pode **recomendar/priorizar** sobre o resultado das regras e explicar em
linguagem natural, mas **não substitui** a decisão determinística nem o registro
auditável.

---

## Justificativa

1. **Explicabilidade é o diferencial, não um detalhe.** Frente a concorrentes
   pipeline/page-centric (LBC §11), o "por que esta próxima ação" é o que vende.
   Só regras versionadas + decision log entregam isso de forma auditável; um
   black-box (Opção C) o destruiria.

2. **Combate explícito ao "Tag → Automação" (LBC §3.2).** O produto existe porque
   automação por tag não lê contexto. O Routing Engine precisa avaliar os 4
   contextos por prioridade — Opção B reintroduziria o problema que o produto
   resolve.

3. **Determinismo + auditabilidade casam com a segurança operacional.** Decisões
   com impacto comercial (enviar para SDR, mudar de jornada) devem ser auditáveis
   (LBC §8.4); regras versionadas dão trilha; a IA fica na camada de recomendação
   (ADR-011), não de decisão silenciosa.

---

## Trade-offs aceitos

- **Perdemos:** a simplicidade do modelo por tag. Justificativa: simplicidade que
  anula o diferencial não é ganho.
- **Perdemos:** a captura automática de padrões sutis do ML. Justificativa: sem
  dados e sem explicabilidade no MVP; a IA entra como recomendação sobre o
  determinístico (ADR-011), preservando auditabilidade. ML pode ser reavaliado em
  V3 (IA preditiva, LBC §7.3) como **sugestão**, nunca como decisor opaco.

---

## Como reverter se a decisão se mostrar errada

**Trocar o runtime de regras (manter explicabilidade):** substituir o motor de
regras por outro (ex.: engine de regras de terceiros) mantendo o contrato do
decision log. **Custo:** semanas; o histórico de decisões permanece.

**Adicionar ML como recomendador (evolução, não reversão):** a saída do ML entra
como **sugestão** ranqueada, ainda registrada no decision log e sujeita à regra
determinística. **Custo:** incremental.

Abandonar a explicabilidade (voltar a tag→automação) **não é reversão aceitável**:
destruiria a proposta de valor — só ocorreria com pivô de produto.

---

## Sinais que indicariam que está errada

- Volume de regras tornando a manutenção/governança inviável (regras conflitantes,
  difícil prever a decisão) de forma recorrente.
- SDRs/closers ignorando o decision log por ser irrelevante/ruidoso (sinal de que
  a explicação não gera confiança — métrica de adoção, Persona 3).
- Decisões de routing exigindo contexto que regras declarativas não capturam,
  comprovadamente, e só ML resolveria — reavaliar então (V3).

---

## Consequências

- **Em código:** `RoutingEngine` (Framing §6.6) avalia 4 contextos por prioridade;
  emite `LeadRouted` + decision log (eventos via Kafka, ADR-008); projeção em
  `routing-decisions-*` (Elastic, ADR-007). RuleEditor/RoutingActionPicker no
  Automation Builder (wireframe TELA 10).
- **Em IA:** Copilot/advisors explicam e recomendam sobre as decisões, citando
  fonte (ADR-002/011); não decidem sozinhos.
- **Em produto:** explicabilidade exposta na UI (wireframe — "por que este lead
  foi roteado").

---

## Referências

- LBC §1 (próxima melhor ação), §3.2 (combate ao tag→automação), §5 (diferencial),
  §8.4 (segurança operacional), §11 (explicabilidade como diferencial competitivo)
- Framing §2.5 (routing explicável), §6.6 (RoutingEngine), §8.2 (fluxo de routing)
- design/wireframe.md TELA 10 (Automation Builder: RuleEditor, RoutingActionPicker)
- Constraints: TECH-005 (event-first), OPS-001
- ADRs relacionados: ADR-008 (reage a/emite eventos), ADR-007 (decision log no Elastic),
  ADR-011 (IA recomenda sobre o determinístico), ADR-002 (explicação via Copilot)
