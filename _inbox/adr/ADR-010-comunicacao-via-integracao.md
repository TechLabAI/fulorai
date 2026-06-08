# ADR-010 — Comunicação multicanal via integração externa (sem motor próprio no MVP)

> **Data:** 2026-06-04
> **Status:** draft (BA)
> **Decisor:** Arquiteto (Danilo Amaral) — pendente de promoção

---

## Contexto

O Journey OS precisa enviar e receber mensagens em WhatsApp, Email, Telegram e
SMS (Communication Hub, COMM — Framing §4.5/§6.8). O LBC §7.3 é explícito:
**no MVP não há motor próprio de Email/WhatsApp** — usa-se integração externa
(Z-API/API oficial WhatsApp, ActiveCampaign/SendGrid). O produto também precisa
de **paridade** com as ferramentas que o infoprodutor já usa (LBC §11.3) e deve
respeitar políticas do WhatsApp (REG-002: opt-in, janela 24h, templates).

A decisão técnica: **construir um motor de entrega de mensagens próprio ou
integrar provedores externos** via um gateway de abstração?

---

## Opções consideradas

### Opção A — Integração externa via CommunicationGateway (DECIDIDA)
- **Vantagens:**
  - Z-API/WhatsApp oficial, ActiveCampaign/SendGrid já resolvem entregabilidade,
    reputação de IP/número, compliance de canal (REG-002) e escala.
  - `CommunicationGateway` (Framing §6.8) abstrai canais atrás de um port: trocar
    provedor não toca o domínio (ADR-004).
  - Paridade com o stack do infoprodutor (LBC §11.3) e foco do MVP no diferencial
    (jornada/routing/receita), não em reinventar entrega de email/WhatsApp.
  - Eventos de entregabilidade (entregue/aberto/respondido) entram como eventos
    de domínio (ADR-008) para alimentar scoring/routing.
- **Desvantagens:**
  - Dependência de terceiros: rate limits, mudanças de API, custo por
    mensagem/assinatura do provedor.
  - **Risco de perda silenciosa** de mensagens/eventos se webhooks falharem —
    mitigado por observabilidade (OPS-001, LBC §12).
- **Custo:** baixo de build; custo recorrente de provedor.

### Opção B — Motor próprio de entrega (SMTP próprio, integração direta WhatsApp Cloud API low-level)
- **Vantagens:**
  - Controle total; sem fee de intermediário; sem rate limit de revenda.
- **Desvantagens:**
  - Entregabilidade de email (reputação de IP, SPF/DKIM/DMARC, warm-up) e
    compliance de WhatsApp são problemas grandes e fora do diferencial.
  - Tempo de build desproporcional para um MVP com time enxuto (ORG-001).
  - Reinventa o que provedores maduros já fazem.
- **Custo:** alto de build e operação; contra o recorte do MVP (LBC §7.3).

### Opção C — Híbrido (motor próprio para um canal, integração para os demais)
- **Vantagens:**
  - Otimiza um canal estratégico mantendo os outros via integração.
- **Desvantagens:**
  - Complexidade de manter dois modelos; sem evidência de que algum canal exija
    motor próprio no MVP/piloto.
- **Custo:** médio; prematuro.

---

## Decisão

Escolhida: **Opção A — comunicação multicanal via integração externa, abstraída
pelo `CommunicationGateway`**, sem motor próprio no MVP.

---

## Justificativa

1. **Recorte explícito do MVP (LBC §7.3).** O escopo já define integração, não
   motor próprio. O diferencial do Journey OS é jornada/routing/receita, não
   entregabilidade — construir motor de email/WhatsApp seria dispersão (risco de
   escopo, LBC §12).

2. **Paridade competitiva por integração (LBC §11.3).** O infoprodutor já usa
   ActiveCampaign/RD/Z-API; integrar reduz atrito de migração (motion consultivo,
   LBC §10) e ancora o valor no que diferencia.

3. **Gateway abstrai o risco de terceiros (ADR-004).** Provedor atrás de um port:
   trocar Z-API por WhatsApp oficial, ou SendGrid por outro, é mudança de adapter,
   não de domínio. Mantém a opção de motor próprio aberta para depois.

---

## Trade-offs aceitos

- **Perdemos:** controle total sobre entrega e custo por mensagem. Justificativa:
  entregabilidade/compliance são problemas maduros resolvidos por provedores;
  reinventá-los não é o diferencial.
- **Perdemos:** independência de terceiros. Justificativa: mitigada pela abstração
  do gateway (troca de provedor barata) e por observabilidade dos webhooks.
- **Perdemos:** otimização fina de um canal. Justificativa: prematuro; nenhum
  canal demonstrou exigir motor próprio no piloto.

---

## Como reverter se a decisão se mostrar errada

Como os canais estão atrás do `CommunicationGateway` (port), introduzir um motor
próprio para um canal = novo adapter que implementa o mesmo port; o domínio e os
demais canais não mudam. **Custo:** semanas para o canal específico (entregabilidade/
compliance), sem refatorar o resto. A abstração foi escolhida justamente para
tornar essa evolução barata.

---

## Sinais que indicariam que está errada

- Custo recorrente dos provedores ultrapassando consistentemente o de um motor
  próprio (quando FIN-001 estiver definido) em volume real.
- Rate limits/instabilidade de provedor causando perda de mensagens/eventos
  recorrente, visível na observabilidade (health de integrações, OPS-001).
- Requisito de produto que nenhum provedor atende e só motor próprio resolve.

---

## Consequências

- **Em código:** `CommunicationGateway` (Framing §6.8) com adapters por provedor
  (Z-API, SendGrid, ActiveCampaign...) via `IntegrationConnectorHub` (§6.14);
  templates e message routing no domínio COMM; eventos de entregabilidade via
  Kafka (ADR-008) → scoring/routing/Elastic.
- **Em compliance:** REG-002 (opt-in, janela 24h, templates aprovados) tratado na
  camada de integração WhatsApp; consentimento (REG-001/LGPD) no domínio Lead.
- **Em operação:** observabilidade obrigatória de webhooks/dead-letters (OPS-001).

---

## Referências

- LBC §7.2/§7.3 (Communication via integração, sem motor próprio no MVP), §10 (motion consultivo),
  §11.3 (paridade de integrações), §12 (risco de escopo e de perda silenciosa)
- Framing §3.1 (COMM via integração), §4.5, §6.8 (CommunicationGateway), §6.14 (IntegrationConnectorHub)
- Constraints: REG-002 (políticas WhatsApp), REG-001 (LGPD), OPS-001, ORG-001
- ADRs relacionados: ADR-004 (gateway via port/adapter), ADR-008 (eventos de entregabilidade),
  ADR-007 (health de integrações no Elastic)
