# INT-SALE-005 — Contrato de eventos a jusante (compra.confirmada → INTL/COMM)

## Contexto
Validar o contrato dos eventos publicados consumidos por INTL (analytics/`revenue-events`), COMM
(pós-venda) e WRKS (auditoria).

## Spec de referencia
- `contracts/hub-integration.md` §2, `contracts/event-contracts.md` §1, SPEC-09

## Escopo
Teste de contrato dos payloads de `compra.confirmada`/`receita.atribuida`/`oportunidade.*`/
`ltv.atualizado` (envelope, headers, schemaVersion); sem PII além de `contatoRef`. SALE não chama
consumidores sincronamente.

## Resultado esperado
Contrato de evento estável e versionável a jusante.

## Criterios de aceite
- [ ] payloads conforme `event-contracts.md` (envelope + headers + schemaVersion)
- [ ] nenhuma PII além de `contatoRef`
- [ ] integração a jusante 100% por evento (sem Feign SALE→INTL/COMM)

## Dependencias
- SALE-015 (precede)

## Estimativa
S

## Prioridade
P6
