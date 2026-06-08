# COMM-011 -- Config de canal API + segredo via credencial_ref

## Contexto
Configuração por empresa de canal/provedor, guardando apenas referência ao segredo (secret manager).

## Spec de referencia
- SPEC-01-api-surface
- SPEC-06-security

## Escopo
- `CanalController`: `POST /api/v1/channels`, `GET /`, `PATCH /{id}`.
- `ConfigCanalService` (`@Transactional`): cria/edita `config_canal` (canal, provedor, identidade_remetente, credencial_ref, janela_envio, ativo).
- `credencial_ref` é referência (`secret://...`/`${VAR}`); segredo nunca persistido/retornado/logado.
- UNIQUE `(canal, provedor)` → 409 `comm.canal.duplicado`.

## Resultado esperado
Empresa configura provedores de canal; segredos ficam fora do banco e das respostas.

## Criterios de aceite
- [ ] `POST /channels` nunca retorna segredo em claro.
- [ ] Config duplicada `(canal, provedor)` → 409 `comm.canal.duplicado`.
- [ ] Disparo para canal sem config ativa → 422 `comm.canal.nao-configurado`.

## Dependencias
- COMM-008 (precede)

## Estimativa
M

## Prioridade
P4
