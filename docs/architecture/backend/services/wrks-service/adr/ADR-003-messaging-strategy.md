# ADR-003 — Estratégia de mensageria (sync evaluate + async eventos via Kafka)

**Status:** accepted

## Contexto

WRKS tem dois perfis de interação: (a) o caminho crítico de autorização, presente em **toda**
request da plataforma, e (b) propagação de mudanças de RBAC e trilha de auditoria, que podem
ser eventuais. Misturar os dois no mesmo mecanismo penaliza latência ou acoplamento.
`project-context.json` define o event bus como **Kafka (AWS MSK)**.

## Decisão

- **Sync (HTTP)** para o caminho crítico: `login`, `refresh`, `logout`, `trocar-empresa`, e `POST /access/evaluate` (com cache Redis). Latência baixa e resposta imediata.
- **Async (Kafka)** para eventos de domínio: `journey-os.modelo.acesso.alterado` (invalidação de cache cross-serviço), `journey-os.usuario.criado`, `journey-os.empresa.provisionada`, `journey-os.sessao.*`.
- **Async consumer (Kafka)** para **auditoria**: WRKS consome todos os eventos `journey-os.*` e grava `evento_auditoria` + indexa em `audit-events`.
- Propagação de contexto em listeners: header `empresaId` na mensagem; `EmpresaContextHolder` populado no consumer e `clear()` em `finally`.

## Alternativas consideradas

- **Tudo síncrono (Feign para invalidar cache de cada serviço)**: acopla WRKS a N serviços e falha em cascata. Rejeitada.
- **AccessDecision por evento (event-sourced) sem HTTP**: latência e complexidade incompatíveis com caminho crítico. Rejeitada.
- **JMS/Artemis** (citado em `platform-patterns.md` legado): substituído por **Kafka** conforme `project-context.json`. (Gap G-5: alinhar docs shared.)

## Consequências

**Positivas:** caminho crítico rápido e isolado; propagação de RBAC desacoplada e resiliente; auditoria não bloqueia produtores.

**Negativas:** dois mecanismos para manter; consistência eventual na invalidação de cache (mitigada por `modelo_acesso_versao` + 401 `versao-desatualizada` — ver ADR-005).

## Referências

- `docs/architecture/shared/multi-empresa.md` (propagação de contexto)
- `docs/architecture/shared/rbac/session-policy.md` (invalidação por versão)
- `04-backend-architecture-direction.md` §6
