# LEAD-002 -- Domain model + ports (Lead, PerfilLead, MaturityScore, RegraQualificacao, Segmento)

## Contexto
Modelo de domínio puro (POJO, zero Spring/JPA) e as portas in/out que definem a fronteira hexagonal.

## Spec de referencia
- SPEC-02-lead-qualification-orchestration
- SPEC-03-maturity-score-6d
- SPEC-04-data-model-migrations

## Escopo
- `domain.model`: `Lead`, `PerfilLead`, `AtributoPerfil`, `Survey`, `Pergunta`, `RespostaSurvey`,
  `RegraQualificacao`, `CondicaoRegra`, `MaturityScore`, `ScoreDimensao`, `Segmento`, `LeadSegmento`.
- Enums: `EstadoQualificacao`, `BaseLegal`, `Dimensao`, `OrigemAtributo`, `TipoAtributo`,
  `TipoPergunta`, `OperadorCondicao`.
- `application.port.in`: casos de uso (capturar, qualificar, responder survey, gerir regra/segmento).
- `application.port.out`: `LeadRepositoryPort`, `SurveyRepositoryPort`, `RegraQualificacaoRepositoryPort`,
  `SegmentoRepositoryPort`, `TechLabQualificationPort`, `LeadSearchPort`, `LeadEventPublisherPort`,
  `AccessDecisionCachePort`.

## Resultado esperado
Domínio compila isolado; nenhuma anotação Spring/JPA em `domain.*` (RULE-01/02).

## Criterios de aceite
- [ ] `domain.*` sem `org.springframework`/`jakarta.persistence` (ArchUnit RULE-01/02).
- [ ] Todas as portas out declaradas como interfaces em `application.port.out`.
- [ ] Invariantes do `03-initial-domain-framing.md` refletidas no modelo.

## Dependencias
- LEAD-001 (precede)

## Estimativa
M

## Prioridade
P1
