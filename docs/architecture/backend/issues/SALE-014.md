# SALE-014 — LGPD (anonimização/expurgo de PII do comprador)

## Contexto
Suportar anonimização e expurgo da PII do comprador em `compra`, preservando valores de receita/LTV.

## Spec de referencia
- SPEC-06, `05-persistence-model.md` §4

## Escopo
Operações de anonimização (limpa `nome_comprador`/`email_comprador`) e expurgo (exceto retenção
fiscal); PII fora de logs/eventos (só `contato_ref`).

## Resultado esperado
Conformidade LGPD sem corromper receita.

## Criterios de aceite
- [ ] anonimizar limpa PII e mantém `valor_total`/agregados
- [ ] expurgo respeita retenção fiscal configurável
- [ ] eventos carregam só `contato_ref` (sem nome/email em claro)

## Dependencias
- SALE-009 (precede)

## Estimativa
M

## Prioridade
P5
