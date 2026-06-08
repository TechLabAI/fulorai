# INT-GWY-004 -- Roteamento p/ serviços de negócio + timeouts/resiliência

## Contexto
Garantir o encaminhamento confiável às 7 famílias de serviço (WRKS/LEAD/JRNY/ASST/COMM/SALE/INTL)
com timeouts por classe de rota e sem retry em métodos mutantes (preserva idempotência).

## Spec de referencia
- contracts/integration-contracts.md (§4, §5)
- SPEC-05-idempotency-concurrency

## Escopo
- Timeouts de conexão/resposta por rota (via `${VAR}`).
- Política de retry: permitido só para métodos idempotentes (GET/HEAD/OPTIONS).
- 504 em timeout de resposta; 503 sem instância.
- (Pós-MVP, documentar) circuit-breaker Resilience4j por `service-id`.

## Resultado esperado
Encaminhamento resiliente e seguro quanto a duplicação.

## Criterios de aceite
- [ ] Timeout de resposta do downstream → 504.
- [ ] Sem instância saudável → 503.
- [ ] Nenhum reenvio automático de POST/PUT/PATCH/DELETE.
- [ ] `Idempotency-Key` do cliente propagado intacto.

## Dependencias
- GWY-002 (precede)
- INT-GWY-001 (Eureka)

## Estimativa
M

## Prioridade
P4
