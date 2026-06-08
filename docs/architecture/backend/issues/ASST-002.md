# ASST-002 -- Domínio: Asset/VersaoAsset/Aprovacao/TagAsset + máquina de estados

## Contexto
Modelo de domínio puro (POJO, zero Spring/JPA) do Asset Hub e o domain service que governa as
transições de estado e as invariantes de versionamento imutável.

## Spec de referencia
- SPEC-02-asset-lifecycle
- SPEC-04-data-model-migrations

## Escopo
- `domain/model`: `Asset` (agregado raiz), `VersaoAsset` (imutável), `Aprovacao`, `TagAsset`;
  value objects `ConteudoComposto`, `ReferenciaBinario`, `BriefComposicao`.
- Enums: `TipoAsset`, `EstadoAsset`, `OrigemVersao`, `EstadoVersao`, `DecisaoAprovacao`, `OrigemTag`.
- `domain/service`: `TransicaoEstadoService` (state machine), `PoliticaVersaoService` (numeração/imutabilidade).
- Invariantes: versão imutável; ≤1 versão vigente; transição válida só pelo agregado raiz.

## Resultado esperado
Regras de domínio testáveis sem Spring; transição inválida lança erro de domínio.

## Criterios de aceite
- [ ] Transições válidas/ inválidas cobertas por testes unitários (sem Spring).
- [ ] `VersaoAsset` não expõe setter de conteúdo (imutável).
- [ ] `:asst-service:architectureCheck` PASS (RULE-01/02 — domínio sem Spring/JPA).

## Dependencias
- ASST-001 (precede)

## Estimativa
M

## Prioridade
P1
