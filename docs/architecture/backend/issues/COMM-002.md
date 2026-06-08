# COMM-002 -- Domínio puro (modelos + state machine de entrega + domain services)

## Contexto
Núcleo de domínio do COMM, sem Spring/JPA: agregados, enums e serviços de domínio (resolução de
roteamento, transição de entrega, render de template).

## Spec de referencia
- SPEC-02-message-dispatch-lifecycle
- SPEC-03-channel-routing
- SPEC-04-data-model-migrations

## Escopo
- Modelos POJO: `TemplateMensagem`, `Mensagem`, `EventoEntrega`, `RegraRoteamento`, `ConfigCanal`.
- Enums: `Canal`, `TipoTemplate`, `EstadoTemplate`, `EstadoEntrega`, `TipoEventoEntrega`, `Provedor`.
- `TransicaoEntregaService` (máquina `PENDENTE→ENFILEIRADA→ENVIADA→ENTREGUE→LIDA`/`FALHADA`, monotônica).
- `RenderTemplateService` (substitui `{{variaveis}}`; valida variável ausente).
- `ResolucaoRoteamentoService` (prioridade + canal preferido + fallback).
- Invariantes: snapshot imutável; transição inválida → erro de domínio; roteamento sem canal → erro.

## Resultado esperado
Regras de entrega/roteamento/render testáveis sem Spring; transições inválidas barradas no domínio.

## Criterios de aceite
- [ ] `domain.*` não importa Spring/JPA (ArchUnit RULE-01/02).
- [ ] Transição inválida (ex.: ENVIADA→PENDENTE) lança erro de domínio.
- [ ] Render com variável ausente sinaliza erro (mapeado a 422 na API).
- [ ] Roteamento sem canal resolvível sinaliza erro (mapeado a 422 na API).

## Dependencias
- COMM-001 (precede)

## Estimativa
L

## Prioridade
P1
