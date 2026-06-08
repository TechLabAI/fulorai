# INT-MIG-001 -- PostgreSQL connectivity + startup retry/fail-fast

## Contexto
MIG depende exclusivamente do cluster PostgreSQL (RDS/Aurora). A conexão deve tolerar
indisponibilidade transitória no startup, mas falhar rápido se persistir.

## Spec de referencia
- contracts/integration-contracts.md
- SPEC-06 (Security — credenciais)

## Escopo
- DataSource configurado via env (`MIG_DB_*`).
- Retry de conexão limitado no startup; após o limite, fail-fast (exit não-zero).
- Sem circuit breaker (migração não é chamada runtime resiliente).

## Resultado esperado
DB transitoriamente indisponível → retry; indisponível além do limite → falha clara.

## Criterios de aceite
- [ ] Conexão estabelecida com credenciais de ambiente.
- [ ] DB indisponível no startup → retry até o limite configurado.
- [ ] Após o limite → exit não-zero com erro claro.
- [ ] Teste de integração (Testcontainers Postgres) cobre o caminho feliz.

## Dependencias
- MIG-001 (precede)

## Estimativa
M

## Prioridade
P1
