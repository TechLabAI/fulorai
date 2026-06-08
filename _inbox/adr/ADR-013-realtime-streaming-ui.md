# ADR-013 — Atualização em tempo real via SSE (Copilot e builders)

> **Data:** 2026-06-04
> **Status:** draft (BA)
> **Decisor:** Sponsor (Danielle Amaral) decidiu o protocolo em 2026-06-04 (D4); arquiteto (Danilo Amaral) fecha o ADR — pendente de promoção

---

## Contexto

A Fase 0.3 (UX) descobriu, e a **TECH-006** registrou, que telas críticas do Journey OS exigem **feedback em tempo real**:

- **Copilot Chat** (wireframe TELA 19): a resposta do assistente deve aparecer de forma fluida (idealmente **streaming token-a-token**), com estado de "recuperando evidência…". A TechLab AI (ADR-002) já produz tokens incrementais que o backend pode repassar.
- **Builders** (Journey Builder TELA 06, Automation Builder TELA 10): feedback de validação, salvamento e progresso (estados loading/erro/validação do wireframe §8).

Em ambos, o fluxo relevante é **servidor → cliente** (push de tokens / push de progresso). O envio da pergunta e as ações de edição continuam sendo **REST normais** (cliente → servidor). Não há, no MVP, co-edição multiusuário ao vivo (que exigiria canal bidirecional).

A decisão de **protocolo** é cara de reverter (afeta backend Java, frontend Angular, infra/ALB) e por isso merece ADR. Decidido por **Danielle Amaral (sponsor) em 2026-06-04 (D4): SSE**, sobre a stack AWS gerenciada já definida (ALB; TECH-007).

---

## Opções consideradas

### Opção A — SSE (Server-Sent Events)
- **Vantagens:** unidirecional servidor→cliente, caso de uso canônico para streaming de LLM e push de progresso; HTTP puro (atravessa proxies/ALB da AWS sem config especial); reconexão nativa; simples no Spring (`SseEmitter`/`Flux`) e no Angular (`EventSource`).
- **Desvantagens:** só servidor→cliente (cliente→servidor segue REST — suficiente para os usos atuais); limite de conexões por navegador em HTTP/1.1 (mitigado por HTTP/2).
- **Custo:** baixo.

### Opção B — WebSocket
- **Vantagens:** bidirecional full-duplex; padrão para colaboração ao vivo / co-edição futura.
- **Desvantagens:** overkill para os usos do MVP (não há co-edição multiusuário); mais complexo (handshake, heartbeat, STOMP); escala com estado e exige config específica no ALB.
- **Custo:** médio-alto.

### Opção C — Polling / long-polling
- **Vantagens:** trivial de implementar; sem infra nova.
- **Desvantagens:** latência ruim para streaming de LLM (não entrega token-a-token fluido); desperdício de requisições; UX inferior nas telas críticas.
- **Custo:** baixo de implementação, alto de UX.

---

## Decisão

Escolhida: **Opção A — SSE** (decisão D4, sponsor 2026-06-04) para todo push
servidor→cliente do MVP: streaming de respostas do Copilot (tokens da TechLab AI)
e feedback de progresso/validação dos builders. Ações do usuário (enviar
pergunta, salvar jornada/automação) permanecem REST.

---

## Justificativa

1. **Os usos do MVP são unidirecionais servidor→cliente** (tokens do Copilot,
   progresso de builder), não canal bidirecional — SSE é o transporte canônico
   para isso; WebSocket seria complexidade sem retorno.
2. **Encaixe na infra AWS gerenciada (TECH-007).** SSE é HTTP puro e atravessa o
   ALB sem a config de upgrade exigida por WebSocket — menor superfície
   operacional para o time pleno sem SRE (ORG-001), dentro do teto de infra
   (FIN-001).
3. **Simplicidade no stack:** Spring (`Flux`/`SseEmitter`) e Angular
   (`EventSource`) suportam SSE diretamente; reconexão automática reduz código de
   resiliência no cliente; integração direta com o `Flux` de tokens da TechLab AI.
4. **Cumpre TECH-006** com o menor custo, mantendo a porta aberta para WebSocket
   se surgir co-edição multiusuário ao vivo.

Polling (C) foi descartado por degradar a UX do streaming do Copilot, que é
diferencial de produto (LBC §11).

---

## Trade-offs aceitos

- **Perdemos (se SSE):** bidirecionalidade nativa — aceitável porque o cliente→servidor é REST e não há co-edição no MVP.
- **Perdemos (se WebSocket):** simplicidade — em troca de um canal que o MVP não usa.
- **Isolamos:** o streaming entra por um **adapter de API** (ADR-004), não pelo domínio — trocar o protocolo no futuro não afeta as regras de negócio.

---

## Como reverter se a decisão se mostrar errada

Como o streaming entra via **adapter de API** (porta de saída do hexágono, ADR-004) e a UI consome por um serviço Angular isolado, trocar o protocolo (ex.: SSE → WebSocket) é localizado: reescrever o adapter de transporte no backend + o serviço de stream no frontend, **sem tocar o domínio** nem os componentes de tela. Custo estimado: dias, não semanas. Como o protocolo ainda não foi implementado (Estágio 0), reverter hoje é custo zero.

---

## Sinais que indicariam que está errada

- Surgimento de requisito de **co-edição multiusuário ao vivo** nos builders (vários usuários no mesmo canvas) → inverteria a favor de WebSocket.
- Limite de conexões SSE por navegador causando falhas com muitas abas/telas simultâneas (mitigado por HTTP/2).
- Latência de streaming do Copilot percebida como ruim pelos usuários (feedback negativo recorrente — KPI-005), mesmo com HTTP/2 e tuning de timeout do ALB.
- Necessidade de canal cliente→servidor de baixa latência e alta frequência (não coberto por REST) tornando-se requisito frequente.

---

## Consequências

- **Em código:** adapter de transporte SSE no backend Java (`SseEmitter`/`Flux<ServerSentEvent>`); serviço de stream no Angular (`EventSource`/client SSE, com reconexão); o domínio permanece intacto (ADR-004).
- **Em IA:** o `AiCopilotOrchestrator` (Framing §6.11) repassa os tokens da TechLab AI (ADR-002) por SSE.
- **Em infra:** ALB da AWS (TECH-007) com timeout de idle ajustado para conexões SSE e HTTP/2 habilitado; sem config de WebSocket.
- **Na TECH-006:** o protocolo deixa de ser `TODO[arquiteto]` — fixado em SSE por este ADR.

---

## Referências

- Constraints: TECH-006 (necessidade de feedback responsivo/streaming), TECH-007 (hospedagem — afeta viabilidade de proxy)
- Framing §6.11 (AiCopilotOrchestrator), §9 (estratégia de IA)
- Wireframe: TELAS 06, 10, 19 (§5.6/§5.10/§5.19), §8 (estados de tela crítica)
- LBC §11 (diferencial de IA), KPI-005 (confiabilidade do Copilot)
- ADRs relacionados: ADR-002 (TechLab AI / tokens), ADR-004 (hexagonal — streaming via adapter), ADR-005 (frontend Angular)
