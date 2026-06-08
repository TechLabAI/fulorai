# Event Catalog — GWY (API Gateway)

> **Nenhum evento de domínio.** O gateway é stateless e de borda; não publica nem consome
> eventos Kafka. Sinais operacionais são expostos como métricas/logs (ver SPEC-07).

| Evento | Tipo | Payload | Consumidores |
|---|---|---|---|
| _(nenhum)_ | — | — | — |

## Justificativa

- O gateway não possui agregados nem transações de domínio (ver `03-initial-domain-framing.md`).
- Auditoria de acesso, se necessária no futuro, será modelada como evento de auditoria do **WRKS**
  (`audit-events`), **não** emitido pelo gateway.
- Decisões de borda (auth negada, rate-limit, rota inexistente) são observáveis via métricas
  Micrometer e logs estruturados com `correlationId`.
