# ADR-004 — Arquitetura hexagonal + monólito modular primeiro

> **Data:** 2026-06-04
> **Status:** draft (BA)
> **Decisor:** Arquiteto (Danilo Amaral) — pendente de promoção

---

## Contexto

O Journey OS tem 7 domínios funcionais (WRKS, LEAD, JRNY, ASST, COMM, SALE,
INTL — Framing §4) com lógica de negócio densa e regras determinísticas
(Maturity Score, progressão de jornada, decision log de routing). Duas decisões
arquiteturais internas precisam ser tomadas:

1. **Padrão interno dos serviços:** hexagonal (ports & adapters) vs N-tier
   tradicional (Controller → Service → Repository)?
2. **Topologia de deploy:** monólito modular único vs microserviços desde já?

O produto é event-first (ADR-008), depende de IA externa (ADR-002), Elastic
(ADR-007) e multi-tenancy (ADR-003) — todos pontos que precisam ser desacoplados
do domínio para serem testáveis e substituíveis. O time é enxuto (ORG-001) e
ainda não há código de produção.

---

## Opções consideradas

### Opção A — Hexagonal + monólito modular primeiro (DECIDIDA)
- **Vantagens:**
  - Domínio puro testável sem infra; IA/Elastic/Kafka/PostgreSQL atrás de ports.
  - Cumpre TECH-001 (padrão do framework, 9 regras ArchUnit, scaffolds).
  - Monólito modular com fronteiras por domínio: deploy/observabilidade simples
    para time enxuto, mas com costuras prontas para **extrair serviços**
    (Journey, Revenue, Communication, AI) quando justificado (Framing §2.6).
- **Desvantagens:**
  - Boilerplate (port + adapter + mapper).
  - Disciplina para manter as fronteiras de módulo dentro do monólito.
- **Custo:** médio inicial, baixa dívida técnica.

### Opção B — N-tier tradicional (Spring MVC clássico)
- **Vantagens:**
  - Curva de aprendizado nula; documentação Spring abundante.
- **Desvantagens:**
  - Acopla domínio à infra (entities JPA, Spring no core) — difícil trocar
    Elastic/Kafka/IA sem tocar regras de negócio.
  - Testes de domínio exigem mockar Spring/Hibernate.
  - Fora do enforcement do framework.
- **Custo:** baixo inicial, alta dívida técnica.

### Opção C — Microserviços desde o início
- **Vantagens:**
  - Escala e deploy independentes por domínio.
- **Desvantagens:**
  - Complexidade operacional (rede, consistência distribuída, observabilidade)
    desproporcional ao MVP e ao time enxuto (ORG-001).
  - Viola o princípio de não introduzir microserviços prematuros (Framing §2.6).
- **Custo:** alto operacional, prematuro antes de PMF.

---

## Decisão

Escolhida: **Opção A — Hexagonal (ports & adapters) + monólito modular primeiro**.

---

## Justificativa

1. **Desacoplar os muitos pontos de variação do Journey OS.** O produto integra
   IA externa (ADR-002), Elastic (ADR-007), Kafka (ADR-008) e PostgreSQL/pgVector
   (ADR-006). Hexagonal coloca cada um atrás de um port — trocar provider de IA,
   adiar Kafka (FIN-001) ou reindexar Elastic não toca o domínio.

2. **Monólito modular casa com o time enxuto e o MVP (ORG-001, LBC §7).** Um
   único deploy observável (OPS-001) entrega as 34 telas P0 mais rápido que
   microserviços, sem perder a opção de extração — as fronteiras de módulo
   (WRKS/LEAD/JRNY/ASST/COMM/SALE/INTL) são as linhas de corte futuras.

3. **Domínio determinístico testável.** Maturity Score (ADR-011) e routing
   (ADR-009) são lógica pura que, isolada por hexagonal, roda em testes
   unitários rápidos sem subir infra.

4. **Cumpre TECH-001 com ferramental pronto** (scaffold + ArchUnit do framework).

---

## Trade-offs aceitos

- **Perdemos:** simplicidade do N-tier. Justificativa: a dívida de acoplamento
  domínio↔infra seria pior dado o número de integrações do produto.
- **Perdemos:** escala/deploy independentes dos microserviços. Justificativa:
  prematuro antes de PMF; o monólito modular preserva o caminho de extração.
- **Perdemos:** menos arquivos por feature. Justificativa: o gerador cria a
  estrutura; custo marginal por feature é baixo.

---

## Como reverter se a decisão se mostrar errada

**Para N-tier:** mover lógica de `application.service` para services diretos,
domínio vira entities JPA, eliminar ports/adapters, desabilitar ArchUnit.
**Custo:** ~2 semanas por módulo; perda de testabilidade.

**Do monólito modular para microserviços (evolução planejada, não reversão):**
extrair um módulo de cada vez pelas fronteiras já definidas, promovendo eventos
internos a tópicos Kafka entre serviços. **Custo:** dias a semanas por serviço
extraído — barato justamente porque hexagonal + módulos foram escolhidos agora.

---

## Sinais que indicariam que está errada

- Devs gastando mais tempo navegando estrutura/escrevendo mappers do que lógica.
- Regras ArchUnit sendo desabilitadas com frequência por exceções.
- Um módulo do monólito (ex.: indexação Elastic, attribution) tornando-se
  gargalo de escala/deploy que força extração antes do previsto — sinal de
  evolução, não de erro do padrão.

---

## Consequências

- **Em código:** cada módulo segue `domain / application(port in,out) /
  infrastructure(adapters) / api`; domínio sem Spring/JPA; 9 regras ArchUnit no
  pipeline; `packageBase = com.journeyos.<modulo>`.
- **Em deploy:** um artefato (monólito) com módulos internos; observabilidade
  única (OPS-001).
- **Em evolução:** extração de Journey/Revenue/Communication/AI quando métricas
  justificarem, pelas fronteiras de módulo.

---

## Referências

- LBC §6.2 (13 módulos conceituais), §7 (MVP em 7 sprints), §12 (escopo/risco)
- Framing §2.6 (hexagonal + monólito modular), §4 (domínios = módulos), §5 (camadas)
- Constraints: TECH-001, ORG-001, OPS-001
- ADRs relacionados: ADR-001 (JVM/Spring), ADR-002 (IA via port), ADR-006 (persistence adapter),
  ADR-007/008 (Elastic/Kafka via adapters), ADR-012 (CQRS-light na application layer)
