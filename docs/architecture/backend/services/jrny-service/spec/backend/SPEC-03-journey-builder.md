# SPEC-03 — Journey Builder (definition + versioning state machine)

> Sub-feature crítica: a definição versionada da jornada e a máquina de estados de publicação.
> ADR-005 (jornada versionada, imutável em runtime), ADR-001 (state machine no domínio).
> Contrato: `contracts/data-model.md`. EARS guide: `docs/architecture/backend/standards/ears-notation.md`.

## Objetivo

Especificar a definição de jornadas (estágios ordenados/tipados + regras versionadas) e a máquina
de estados `RASCUNHO → PUBLICADA → ARQUIVADA`, garantindo que uma jornada PUBLICADA seja imutável
em runtime (alterar = nova `versao`) e que inscrições ativas não mudem de definição embaixo do lead.

## Escopo

- **In:** criação/edição de jornada e estágios (só em RASCUNHO), definição de regras, transições de publicação/arquivamento, nova versão, validação de gramática de `condicao`, seed de jornadas default por tenant.
- **Out:** avaliação/decisão de roteamento (SPEC-02), persistência detalhada (SPEC-04), editor visual drag-and-drop (FE/pós-MVP).

## Decisões técnicas

- State machine de jornada no `domain/service/EstadoJornadaService` (POJO, testável sem Spring — ADR-001).
- Transições transacionais no `application/service` (`PublicarJornadaService`, `ArquivarJornadaService`, `CriarNovaVersaoService`); evento via outbox.
- **Imutabilidade em runtime:** PUBLICADA não é editada in-place; `nova-versao` clona em RASCUNHO com `versao+1` (ADR-005).
- Estágios só editáveis enquanto a jornada está RASCUNHO; `(jornada_id, ordem)` único.
- Validação da gramática de `condicao` (campos do snapshot LEAD) no momento da definição da regra (`data-model.md` §5).

## Máquina de estados

```
            criar                 publicar (tem estágio)        arquivar
   (∅) ──────────────► RASCUNHO ──────────────────────► PUBLICADA ──────────► ARQUIVADA
                          ▲                                  │ nova-versao
                          └──────────── nova-versao ─────────┘  (RASCUNHO versao+1; PUBLICADA intacta)
   qualquer estado ── arquivar ──► ARQUIVADA (soft; não roteia novos leads)
```

## Implementação

- `CriarJornadaService`, `EditarJornadaService` (guarda RASCUNHO), `AdicionarEstagioService`, `DefinirRegraService`, `PublicarJornadaService`, `ArquivarJornadaService`, `CriarNovaVersaoService`.
- Seed de jornadas/estágios default ao consumir `journey-os.empresa.provisionada` (idempotente).

## Casos de borda

- Editar jornada PUBLICADA in-place → 409 `jrny.jornada.transicao-invalida`.
- Publicar jornada sem estágio → 422 `jrny.jornada.sem-estagio`.
- Estágio com ordem duplicada → 409 `jrny.estagio.ordem-duplicada`.
- Nova versão de PUBLICADA → RASCUNHO `versao+1`; inscrições ativas seguem na versão de entrada.
- Arquivar jornada → não matricula/roteia novos leads; estágios/regras/decisões preservados.

## Critérios de aceite (EARS)

- `WHEN a journey is created, THE SYSTEM SHALL set estado=RASCUNHO and versao=1.`
- `WHILE a journey is in RASCUNHO, THE SYSTEM SHALL allow editing its metadata, stages and rules.`
- `IF an in-place edit targets a PUBLICADA journey, THEN THE SYSTEM SHALL reject with 409 error.code 'jrny.jornada.transicao-invalida'.`
- `WHEN publish is requested on a RASCUNHO journey with at least one stage, THE SYSTEM SHALL set estado=PUBLICADA and emit journey-os.jornada.publicada.`
- `IF publish is requested on a journey with no stage, THEN THE SYSTEM SHALL reject with 422 error.code 'jrny.jornada.sem-estagio'.`
- `WHEN a new version is requested on a PUBLICADA journey, THE SYSTEM SHALL create a RASCUNHO copy with versao+1 AND SHALL NOT mutate the published version or any active enrolment.`
- `THE SYSTEM SHALL enforce a unique (jornada_id, ordem) per journey so no two stages share a position.`
- `THE SYSTEM SHALL keep tipo_estagio within { CAPTURA, NUTRICAO, QUALIFICACAO, OFERTA, FECHAMENTO, POS_VENDA }.`
- `WHILE a journey is ARQUIVADA, THE SYSTEM SHALL NOT enroll or route any new lead into it AND SHALL preserve its stages, rules and decisions.`
- `IF a rule's condicao references a field outside the documented snapshot grammar, THEN THE SYSTEM SHALL reject the rule definition with 422 error.code 'jrny.regra.condicao-invalida'.`
- `WHEN journey-os.empresa.provisionada is consumed, THE SYSTEM SHALL seed default journeys/stages for the tenant idempotently.`
