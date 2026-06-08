# JRNY-004 -- RotearLeadService: avaliação determinística + matrícula/avanço de inscrição

## Contexto
Caso de uso central (golden path) do Routing Engine, disparado por eventos de LEAD. Carrega a
jornada PUBLICADA aplicável + a `InscricaoJornada` do lead (cria se ausente), invoca o
`MotorRoteamento` e avança a inscrição quando o resultado é `ROTEADO`.

## Spec de referencia
- SPEC-02-routing-engine-orchestration
- SPEC-09-messaging-architecture

## Escopo
- `RotearLeadService.rotear(gatilho, snapshotLead)`: resolve jornada PUBLICADA + inscrição;
  monta `SnapshotLead` do payload; chama `MotorRoteamento`; persiste exatamente **uma** decisão.
- `RotearLeadService.avancarEstagio`: aplica a transição na `InscricaoJornada` (estágio corrente),
  detecta estágio terminal → marca inscrição `CONCLUIDA`.
- Matrícula idempotente (guard partial-unique `(lead_id, jornada_id) WHERE estado='ATIVA'`).
- Sem regra aplicável → resultado `NAO_ROTEADO`; score/segmento sem disparo → `SEM_MUDANCA`.
- `@Transactional` apenas neste service (RULE-03).

## Resultado esperado
Dado `lead.qualificado`, o serviço matricula/avalia/roteia o lead e deixa a inscrição no estágio-alvo,
de forma determinística e reproduzível.

## Criterios de aceite
- [ ] `lead.qualificado` → matrícula criada (se ausente) + avaliação + 1 decisão persistida.
- [ ] Regra de maior prioridade satisfeita decide o estágio-alvo.
- [ ] Estágio terminal → inscrição `CONCLUIDA`.
- [ ] Reprocessar o mesmo evento não duplica matrícula nem decisão.

## Dependencias
- JRNY-002 (precede)
- JRNY-003 (jornada/estágios disponíveis)

## Estimativa
L

## Prioridade
P2
