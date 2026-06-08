# Event Catalog — intl-service (INTL)

| Evento | Tipo | Payload | Consumidores conhecidos |
|---|---|---|---|
| `journey-os.copilot.resposta.gerada` | publicado (âncora) | [event-contracts §1.1](../contracts/event-contracts.md) | INTL (`ai-copilot-events`), WRKS (auditoria) |
| `journey-os.asset.versao.publicada` | consumido | (contrato ASST) | INTL (ingestão de conhecimento) |
| `journey-os.empresa.provisionada` | consumido | (contrato WRKS) | INTL (seed base/índices) |
| `journey-os.modelo.acesso.alterado` | consumido | (contrato WRKS) | INTL (invalida cache AccessDecision) |

> Projeções Elastic (escrita própria de INTL): `journey-os_ai-copilot-events` (fact),
> `journey-os_knowledge-nodes` (dimension). INTL **lê** os demais `journey-os_*` (facts dos
> módulos) para analítica, mas **não** os escreve (ADR-003).
