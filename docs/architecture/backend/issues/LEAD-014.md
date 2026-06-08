# LEAD-014 -- LGPD: base legal, anonimização e expurgo do lead

## Contexto
Conformidade LGPD sobre a PII do lead: base legal obrigatória, anonimização (estado terminal) e
expurgo físico (direito ao esquecimento).

## Spec de referencia
- SPEC-06-security
- SPEC-04-data-model-migrations

## Escopo
- `base_legal` obrigatória na captura (LEAD-004).
- `POST /leads/{id}/anonimizar`: limpa PII de `lead`/`perfil_lead`/`atributo_perfil`, estado `ANONIMIZADO`,
  preserva `maturity_score`/`score_dimensao`.
- `DELETE /leads/{id}` (expurgo): remoção física + trilha em auditoria (payload sem PII).
- Bloqueia edição de lead `ANONIMIZADO` (409 `lead.lead.anonimizado`).
- Logs/eventos sem PII (apenas identificadores).

## Resultado esperado
Lead anonimizado/expurgado conforme LGPD, sem perder integridade dos agregados de score.

## Criterios de aceite
- [ ] Anonimização limpa PII e mantém score; estado `ANONIMIZADO`.
- [ ] Edição de lead anonimizado → 409 `lead.lead.anonimizado`.
- [ ] Expurgo remove fisicamente e registra auditoria sem PII.
- [ ] Nenhuma PII em logs/eventos (apenas IDs).

## Dependencias
- LEAD-004 (captura)
- LEAD-009 (persistência)

## Estimativa
M

## Prioridade
P5
