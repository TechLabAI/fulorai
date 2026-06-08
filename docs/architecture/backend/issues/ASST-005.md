# ASST-005 -- Approval workflow: submit / approve / reject

## Contexto
Golden path da máquina de aprovação: submeter um rascunho à revisão e aprovar/rejeitar,
registrando a decisão.

## Spec de referencia
- SPEC-02-asset-lifecycle
- SPEC-01-api-surface

## Escopo
- `SubmeterAssetService` (`RASCUNHO → EM_REVISAO`), `AprovarAssetService` (`EM_REVISAO → APROVADO|REJEITADO`).
- `AssetApprovalController`: `POST /{id}/submit`, `POST /{id}/approve`.
- Persistir `aprovacao` (revisor, decisão, comentário) em toda transição de revisão.
- Emitir `journey-os.asset.aprovado` / `journey-os.asset.rejeitado` (via outbox — ver ASST-014).

## Resultado esperado
Asset transita rascunho→revisão→aprovado/rejeitado com trilha de aprovação.

## Criterios de aceite
- [ ] submit fora de RASCUNHO → 409 `asst.estado.transicao-invalida`.
- [ ] approve/reject fora de EM_REVISAO → 409.
- [ ] approve grava exatamente uma `aprovacao` com identidade do revisor.
- [ ] reject emite `asset.rejeitado` com comentário.

## Dependencias
- ASST-004 (precede)

## Estimativa
M

## Prioridade
P2
