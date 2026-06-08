# LEAD-006 -- Maturity Score (6D) domain: MaturityScoreCalculator + QualificationRuleEngine

## Contexto
Núcleo determinístico e explicável do score, em `domain.service` (POJO puro). Calcula as 6
dimensões + agregado + breakdown, com idempotência por `(lead_id, versao_regra, hash_sinais)`.

## Spec de referencia
- SPEC-03-maturity-score-6d
- SPEC-05-idempotency-concurrency

## Escopo
- `QualificationRuleEngine`: avalia `condicao_regra` sobre os sinais do perfil → contribuições por dimensão.
- `MaturityScoreCalculator`: agrega as 6 dimensões (`PERFIL/ENGAJAMENTO/INTENCAO/CAPACIDADE/URGENCIA/ADERENCIA`)
  em [0..100], produz `ScoreDimensao[]` (breakdown com contribuintes) e o `hash_sinais`.
- Registro como `@Bean` via `DomainServiceConfig` (domain services são POJO).
- Merge de contribuições da TechLab AI (LEAD-010) marcadas `assist_ia`; nunca causa única de transição.

## Resultado esperado
Mesma entrada → mesmo score (determinístico); breakdown explica cada dimensão.

## Criterios de aceite
- [ ] 6 dimensões calculadas, cada uma em [0,100]; agregado em [0,100].
- [ ] Breakdown registra as condições que contribuíram.
- [ ] Recalcular com mesmos sinais/versão é idempotente (sem novo `maturity_score`).
- [ ] Contribuição de assist IA nunca é a única causa de `QUALIFICADO`/`NAO_QUALIFICADO`.
- [ ] `domain.*` sem Spring/JPA (RULE-01/02); `DomainServiceConfig` presente.

## Dependencias
- LEAD-002 (precede)

## Estimativa
L

## Prioridade
P2
