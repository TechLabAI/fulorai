# ASST-010 -- Asset Intelligence: classificação/tagging via TechLab AI

## Contexto
Sugestão automática de tags/classificação de assets na criação/publicação, best-effort.

## Spec de referencia
- SPEC-03-asset-studio-composition
- SPEC-10-integrations

## Escopo
- Estender `ComposicaoIaPort` (ou novo port) para classificação; chamada best-effort não bloqueante.
- Persistir tags sugeridas em `tag_asset` com `origem=IA`.
- Disparo na criação do asset e na publicação.

## Resultado esperado
Assets ganham tags IA sem bloquear o fluxo principal; ausência de IA não falha a operação.

## Criterios de aceite
- [ ] Tags IA persistidas com `origem=IA` (unicidade `(asset_id, valor)`).
- [ ] Classificação indisponível → operação principal prossegue (best-effort).

## Dependencias
- ASST-009 (precede); INT-ASST-003

## Estimativa
M

## Prioridade
P4
