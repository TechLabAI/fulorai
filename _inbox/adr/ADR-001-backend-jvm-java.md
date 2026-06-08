# ADR-001 — Backend em JVM (Java 21 + Spring, hexagonal)

> **Data:** 2026-06-04
> **Status:** draft (BA)
> **Decisor:** Arquiteto (Danilo Amaral) — pendente de promoção

---

## Contexto

O Journey OS é um SaaS B2B multi-tenant, event-first, com domínios densos
(Lead Intelligence, Qualification, Journey, Routing, Asset, Communication,
Sales/Revenue, Intelligence/Platform — Framing §4). Cada domínio tem
invariantes de negócio reais (Maturity Score multidimensional, regras de
progressão/regressão de jornada, decision log de routing) que precisam de
tipagem forte, testabilidade e um ecossistema maduro de multi-tenancy,
mensageria e observabilidade.

O PRD original (§10) propunha **NestJS (Node/TypeScript)**. Essa stack foi
**descartada** (EXC-001) em favor do alinhamento com o framework
`techlab-architecture`, cujo gerador `new-project.py` produz scaffolds
Java 21 + Spring hexagonais. A decisão técnica aqui é: **qual runtime/linguagem
para o backend de domínio do Journey OS?**

Contexto adicional: a IA roda em serviço dedicado Python (`techlab-ai`,
ADR-002), o que impõe uma arquitetura multi-runtime de qualquer forma — o
backend de domínio não precisa ser Python por causa da IA.

---

## Opções consideradas

### Opção A — Java 21 sobre JVM + Spring (hexagonal)
- **Vantagens:**
  - Alinhamento direto com `techlab-architecture` (gerador `new-project.py`,
    templates Java/Spring hexagonais, regras ArchUnit) — cumpre TECH-001.
  - Ecossistema maduro para multi-tenancy schema-per-empresa (Hibernate schema
    resolver), Kafka (Spring Kafka), outbox transacional, Elastic (clients
    oficiais) e observabilidade (Micrometer/Elastic APM) — exatamente os motores
    do Journey OS (ADR-006/007/008).
  - Tipagem estática forte para domínios densos (scoring, routing, attribution).
- **Desvantagens:**
  - Mais verboso que Node/Kotlin.
  - Footprint de memória maior que Go.
- **Custo:** zero adicional — é o stack do framework.

### Opção B — Node.js / NestJS (TypeScript) — stack do PRD §10
- **Vantagens:**
  - Mesma linguagem do frontend (compartilha tipos/DTOs).
  - Stack originalmente especificada no PRD; familiaridade do mercado infoproduto.
- **Desvantagens:**
  - Fora do framework `techlab-architecture` — perderia gerador, templates e
    enforcement arquitetural (reescrever ferramental).
  - Multi-tenancy schema-per-empresa e outbox transacional são menos
    estabelecidos no ecossistema Node que em Spring/Hibernate.
  - Tipagem estrutural (TS) menos robusta que nominal/estática da JVM para
    invariantes de domínio.
- **Custo:** alto (descartar ferramental do framework) — formalizado em EXC-001.

### Opção C — Go (ou Kotlin sobre JVM)
- **Vantagens:**
  - Go: performance/footprint excelentes, concorrência nativa. Kotlin: conciso,
    null-safety, 100% interop com bibliotecas Java.
- **Desvantagens:**
  - Go: ecossistema enterprise de multi-tenancy/ORM mais fraco; fora do framework.
  - Kotlin: framework `techlab-architecture` não tem templates Kotlin; ramp-up
    e adaptação de scaffolds.
  - Time enxuto (ORG-001) sem necessidade de assumir custo de stack não-default.
- **Custo:** alto (sem suporte do framework, retrabalho de ferramental).

---

## Decisão

Escolhida: **Opção A — Java 21 sobre JVM + Spring, arquitetura hexagonal**.

---

## Justificativa

Três razões dominantes específicas ao Journey OS:

1. **Os motores centrais do produto vivem no ecossistema JVM.** Journey OS
   depende simultaneamente de Kafka (ADR-008), outbox transacional, Elastic
   (ADR-007), pgVector/PostgreSQL (ADR-006) e observabilidade desde o MVP
   (OPS-001). Spring oferece integração de primeira classe para todos esses
   motores; reconstruir essa malha em outro runtime seria o caminho mais caro
   do projeto.

2. **Domínios densos exigem tipagem forte e testabilidade.** Maturity Score
   (6 dimensões, ADR-011), regras de jornada e decision log de routing
   (ADR-009) são lógica determinística pura que se beneficia de domínio Java
   isolado por ports & adapters (ADR-004) e testável sem infraestrutura.

3. **Time enxuto + framework gerador (ORG-001 / TECH-001).** Com Danilo
   produzindo e sem time de dev dedicado ainda, adotar o stack que o
   `new-project.py` gera elimina trabalho de scaffolding e mantém o caminho de
   menor atrito até o MVP.

A IA permanece em Python (`techlab-ai`, ADR-002); a bridge é HTTP REST. A
arquitetura multi-runtime é consciente e desejada.

---

## Trade-offs aceitos

- **Perdemos:** unificação de linguagem com o frontend Angular/TS. Justificativa:
  o ganho de ecossistema/multi-tenancy/eventos na JVM supera o custo de manter
  dois conjuntos de tipos; DTOs são contrato HTTP versionado.
- **Perdemos:** a stack NestJS originalmente especificada no PRD. Justificativa:
  EXC-001 — alinhamento ao framework vale mais que aderência ao PRD obsoleto.
- **Perdemos:** menor footprint de memória de Go. Justificativa: improvável ser
  gargalo antes de PMF; custo de manter a opção aberta não compensa hoje.

---

## Como reverter se a decisão se mostrar errada

Reverter para Node/NestJS (ou outro runtime) implicaria:
1. Reescrever os serviços de domínio já implementados no novo runtime.
2. Reimplementar a malha de multi-tenancy, outbox→Kafka e indexação Elastic.
3. Abandonar/adaptar gerador e templates do `techlab-architecture`.

**Custo estimado:** 4-8 meses de 1-2 devs full-time + congelamento de roadmap.
**Caminho concreto:** só faz sentido se múltiplos sinais abaixo ocorrerem
juntos; antes disso, refatorar dentro da JVM é preferível. Como ainda **não há
código de produção** (Estágio 0), a reversão hoje custa ~zero — a janela barata
de mudança fecha quando o MVP começar a ser codificado.

---

## Sinais que indicariam que está errada

- Throughput de eventos (outbox→Kafka→consumers) abaixo do SLA mesmo após
  tuning de JVM/Spring, de forma consistente por >30 dias.
- Custo de RAM em produção tornando o hosting inviável (>2x do orçamento de
  infra, quando FIN-001 for definido).
- Time alocado para o MVP sem experiência Java e ramp-up bloqueando a entrega
  das 34 telas P0.

---

## Consequências

- **Em código:** serviços de domínio em Java 21 + Spring Boot; `packageBase =
  com.journeyos`; build via gerador do framework.
- **Em arquitetura:** comunicação interna via eventos (Kafka, ADR-008) e REST;
  `techlab-ai` (Python) consumido via HTTP REST (ADR-002).
- **Em time:** critério de contratação Java + Spring; onboarding usa
  documentação do framework.

---

## Referências

- LBC §1, §6 (produto SaaS multi-tenant event-first), §12 (risco de stack)
- Framing §2.6 (hexagonal + monólito modular), §5 (camadas), §11 (stack)
- Constraints: TECH-001, EXC-001, ORG-001
- ADRs relacionados: ADR-002 (IA em Python), ADR-004 (hexagonal), ADR-006/007/008
  (motores que vivem na JVM), ADR-005 (frontend Angular)
