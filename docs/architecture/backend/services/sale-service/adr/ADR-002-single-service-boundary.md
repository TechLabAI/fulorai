# ADR-002 — Single-service boundary (sem decomposição no MVP)

**Status:** accepted

## Contexto

SALE cobre cinco subdomínios relacionados — pipeline/CRM, ofertas, compras/receita, atribuição e
LTV. Há a tentação de separar "CRM" de "billing/receita" em serviços distintos desde o início.
No MVP, porém, todos compartilham o mesmo contexto transacional curto no `emp_<slug>` e o mesmo
gatilho central (`compra.confirmada`), que encadeia reconhecimento de receita → atribuição → LTV.

## Decisão

Manter **um único serviço** `sale-service` (`type: standard`), com o domínio organizado em
agregados (`Oportunidade`, `Oferta`, `Compra`, `Atribuicao`, `Ltv`) dentro do mesmo bounded context.
A coesão do golden path (oportunidade → compra → receita atribuída → LTV) favorece um serviço único.

## Alternativas consideradas

- **CRM separado de Receita/Billing**: melhor isolamento de evolução, mas introduz coordenação
  distribuída (saga) entre `oportunidade.ganha` e `compra.confirmada` sem ganho no MVP. Rejeitada;
  registrada como evolução possível se o volume/equipe justificar.
- **Motor de atribuição como serviço dedicado**: faz sentido se a atribuição virar data-driven/ML;
  no MVP é determinística e cabe no domínio. Rejeitada por ora.

## Consequências

**Positivas:** transação curta e coesa; sem complexidade distribuída no fluxo de receita; deploy
e ArchUnit únicos.

**Negativas:** o serviço acumula responsabilidades; se um subdomínio crescer muito (ex.: billing),
será necessário reavaliar a fronteira (nova ADR). Aceito no horizonte do MVP.

## Referências

- `04-backend-architecture-direction.md` (§2 Service Boundary)
- ADR-001 (hexagonal) · ADR-005 (atribuição/receita)
