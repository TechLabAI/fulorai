# JRNY-005 -- Decision log imutável (DecisaoRoteamento) + resultados ROTEADO/SEM_MUDANCA/NAO_ROTEADO

## Contexto
Toda decisão do Routing Engine grava uma `DecisaoRoteamento` **imutável** com o `snapshot_entrada`
que a originou, a regra disparada e o estado do assist de IA — a trilha do "por quê" (decision log).

## Spec de referencia
- SPEC-02-routing-engine-orchestration
- SPEC-05-idempotency-concurrency

## Escopo
- Persistência da decisão no mesmo `@Transactional` do roteamento (consistência com o avanço).
- Campos: `gatilho`, `snapshot_entrada` (jsonb), `regra_id` (nullable), `assist_ia`
  (`USADO`/`IGNORADO`/`INDISPONIVEL`), `resultado` (`ROTEADO`/`SEM_MUDANCA`/`NAO_ROTEADO`),
  `estagio_alvo_id` (nullable), `motivo`, `decidido_em`.
- Imutabilidade: nenhuma operação de update na decisão; correção = nova decisão.
- CHECK `resultado=ROTEADO ⇒ estagio_alvo_id NOT NULL` garantido (DB + domínio).
- `SEM_MUDANCA`/`NAO_ROTEADO` são registrados mas **não** emitem `lead.roteado`.

## Resultado esperado
Para qualquer lead, o histórico de decisões é recuperável e explica cada movimento (ou não-movimento),
com proveniência do snapshot e da regra/assist.

## Criterios de aceite
- [ ] Toda chamada de roteamento grava exatamente uma decisão.
- [ ] Decisão nunca sofre update (tentativa → erro/ausência de método).
- [ ] `ROTEADO` sempre tem `estagio_alvo_id`; `NAO_ROTEADO`/`SEM_MUDANCA` têm `estagio_alvo_id` nulo.
- [ ] `snapshot_entrada` reflete score/dimensões/segmento usados na avaliação.

## Dependencias
- JRNY-004 (precede)

## Estimativa
M

## Prioridade
P2
