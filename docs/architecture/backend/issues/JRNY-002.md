# JRNY-002 -- Domínio puro: Jornada/Estagio/RegraRoteamento/Inscricao/Decisao + state machines + MotorRoteamento

## Contexto
Núcleo de domínio do JRNY, sem Spring/JPA (RULE-01/02). Modela as duas raízes de agregado
(`Jornada`, `InscricaoJornada`), as entidades filhas (`Estagio`, `RegraRoteamento`,
`DecisaoRoteamento` imutável), as máquinas de estado e o `MotorRoteamento` (avaliação
determinística de regras).

## Spec de referencia
- SPEC-02-routing-engine-orchestration
- SPEC-03-journey-builder
- SPEC-04-data-model-migrations

## Escopo
- `domain/model/`: `Jornada` (estadoJornada, versao), `Estagio` (ordem, tipoEstagio, terminal, config),
  `RegraRoteamento` (condicao, prioridade, versao, ativa), `InscricaoJornada` (estagioCorrente, estado),
  `DecisaoRoteamento` (imutável: gatilho, snapshotEntrada, assistIa, resultado, estagioAlvo, motivo).
- Enums: `EstadoJornada`, `TipoEstagio`, `EstadoInscricao`, `AssistIa`, `ResultadoRoteamento`.
- `domain/service/`: `MotorRoteamento` (avalia regras ordenadas por `prioridade`, retorna decisão),
  `TransicaoEstagioService` (state machine de inscrição), `AvaliadorCondicao` (predicado sobre snapshot do lead).
- Value objects: `CondicaoRoteamento`, `SnapshotLead`, `RecomendacaoIa`.
- Invariantes (doc 03 §5): decisão imutável; ≤1 inscrição ATIVA por (lead, jornada); inscrição referencia `jornadaVersao`; só `PUBLICADA` roteia; transição inválida → erro de domínio.

## Resultado esperado
Domínio compila e é testável por unit tests JUnit sem contexto Spring; avaliação de regras
reprodutível (mesmo snapshot + versão de regras → mesma decisão).

## Criterios de aceite
- [ ] Zero import de `org.springframework`/`jakarta.persistence` em `domain.*` (ArchUnit).
- [ ] `MotorRoteamento` retorna `ROTEADO`/`SEM_MUDANCA`/`NAO_ROTEADO` deterministicamente.
- [ ] Transição de estado inválida lança exceção de domínio (nunca estado corrompido).
- [ ] Unit tests cobrem ordenação por prioridade e ausência de regra aplicável.

## Dependencias
- JRNY-001 (precede)

## Estimativa
L

## Prioridade
P1
