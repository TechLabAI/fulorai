# SPEC-02 — Asset Lifecycle & Approval (core orchestration)

> Núcleo do domínio (evento-âncora: **asset publicado**). ADR-005. EARS guide linkado.

## Objetivo

Especificar a máquina de estados do asset (rascunho → revisão → aprovado/rejeitado → publicado
→ arquivado) e as invariantes de versionamento imutável.

## Escopo

- **In:** transições de estado, criação de versão imutável, registro de aprovação, promoção da versão vigente, emissão de eventos.
- **Out:** composição IA (SPEC-03), persistência detalhada (SPEC-04), mensageria (SPEC-09).

## Decisões técnicas

- State machine no `domain/service/TransicaoEstadoService` (POJO, testável sem Spring — ADR-001).
- Versões imutáveis (copy-on-write) — ADR-005.
- Transições transacionais no `application/service` (`@Transactional` — RULE-03); evento via outbox.

## Máquina de estados

```
RASCUNHO --submit--> EM_REVISAO --approve(APROVADO)--> APROVADO --publish--> PUBLICADO
   ^                     |                                                       |
   | nova versão         | approve(REJEITADO)                                    |
   |                     v                                                       |
   +------------------ REJEITADO                                                 |
PUBLICADO --nova versão (compose/editar)--> RASCUNHO (numero+1)                  |
qualquer --arquivar--> ARQUIVADO (soft)                                          |
```

## Implementação

- `SubmeterAssetService`, `AprovarAssetService`, `PublicarAssetService`, `CriarAssetService`, `CriarVersaoService`.
- Publicar promove `versao_vigente_id` para a versão aprovada; versão anterior preservada.

## Casos de borda

- Submeter asset sem versão de rascunho → 409.
- Aprovar/rejeitar fora de EM_REVISAO → 409.
- Publicar fora de APROVADO → 409.
- Publicar nova versão de asset já publicado → atualiza vigente sem apagar a anterior.

## Critérios de aceite (EARS)

- `WHEN submit is requested on a RASCUNHO asset that has a draft version, THE SYSTEM SHALL transition it to EM_REVISAO.`
- `IF a transition is requested from a state that does not allow it, THEN THE SYSTEM SHALL reject with 409 error.code 'asst.estado.transicao-invalida' AND SHALL NOT mutate the asset.`
- `WHEN approve with decisao=APROVADO is requested on an EM_REVISAO asset, THE SYSTEM SHALL move it to APROVADO and persist exactly one aprovacao record.`
- `WHEN approve with decisao=REJEITADO is requested, THE SYSTEM SHALL move it to REJEITADO and emit journey-os.asset.rejeitado.`
- `WHEN publish is requested on an APROVADO asset, THE SYSTEM SHALL set the approved version as versao_vigente_id, set estado=PUBLICADO, and emit journey-os.asset.versao.publicada.`
- `THE SYSTEM SHALL preserve every previously published version when a newer version is published.`
- `IF a client attempts to mutate an existing versao_asset, THEN THE SYSTEM SHALL reject with 409 error.code 'asst.versao.imutavel'.`
