# COMM-005 -- Disparo (aceite assíncrono): POST /messages → render + enfileirar

## Contexto
Aceite de um pedido de disparo: valida, renderiza o conteúdo (snapshot imutável), persiste em
PENDENTE, grava outbox e retorna 202 ENFILEIRADA.

## Spec de referencia
- SPEC-02-message-dispatch-lifecycle
- SPEC-01-api-surface

## Escopo
- `MensagemController`: `POST /api/v1/messages`, `GET /{id}`, `GET /`, `GET /{id}/events`.
- `MensagemService` (`@Transactional`): resolve canal (COMM-004), renderiza (COMM-002), persiste `Mensagem` PENDENTE, grava `EventoEntrega(ENFILEIRADA)` + outbox; retorna 202.
- Validações: template não-ATIVO → 409 `comm.template.nao-ativo`; variável ausente → 422; canal não configurado → 422.

## Resultado esperado
Disparo aceito vira `Mensagem` ENFILEIRADA com conteúdo renderizado imutável; envio é assíncrono.

## Criterios de aceite
- [ ] Disparo válido → 202 + `estadoEntrega=ENFILEIRADA` + Location.
- [ ] Template não-ATIVO → 409 `comm.template.nao-ativo`.
- [ ] `conteudo_renderizado` é snapshot (não muda se o template for editado depois).
- [ ] Evento `journey-os.mensagem.enfileirada` gravado em outbox na mesma TX.

## Dependencias
- COMM-004 (precede)

## Estimativa
M

## Prioridade
P2
