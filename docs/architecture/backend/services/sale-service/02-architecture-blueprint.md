# 02 — Architecture Blueprint — SALE (Sales & Revenue)

> Como o SALE se conecta ao mundo e como se organiza por dentro. Não é código — é fronteira.

## 1. System Boundary

SALE é um microserviço **standard** (Spring Boot, hexagonal) dono dos agregados **Oportunidade**
(pipeline/CRM), **Oferta** (catálogo), **Compra** (pedido/receita), **Atribuição** (receita→touchpoints)
e **LTV**, dentro do schema operacional `emp_<slug>` de cada empresa. Expõe API REST sob
`/api/v1/oportunidades/**`, `/api/v1/ofertas/**`, `/api/v1/compras/**`, `/api/v1/atribuicao/**`
e `/api/v1/ltv/**`. Não é dono de identidade (WRKS), qualificação (LEAD), roteamento (JRNY) nem
comunicação (COMM); **não** processa pagamento (gateway externo).

```
            ┌─────────────────────────────────────────────────────────┐
            │                      sale-service                        │
   JWT ───▶ │  api  ─▶ application ─▶ domain ◀─ infrastructure         │
 (via GWY)  │                                  │  ├─ persistence (PG)   │
            │                                  │  ├─ messaging (Kafka)  │
            │                                  │  └─ search (Elastic)   │
            └─────────────────────────────────────────────────────────┘
```

## 2. External Actors and Systems

| Ator / Sistema | Tipo | Interação |
|---|---|---|
| **GWY (API Gateway)** | entrada | Roteia chamadas autenticadas; injeta JWT/contexto. |
| **WRKS** | dependência sync + eventos | `AccessDecision` (Feign) para autorização `sale.*`; consome `empresa.provisionada` (seed pipeline/ofertas) e `modelo.acesso.alterado` (cache). |
| **LEAD** | dependência por eventos | Consome `lead.qualificado` / `lead.score.atualizado` → cria/prioriza `oportunidade`. SALE **não** chama LEAD por Feign no fluxo de venda. |
| **Checkout / gateway externo** (Hotmart, link de pagamento) | fonte de compra | Pedido confirmado entra via `POST /api/v1/compras` (idempotente por `id_externo`) no MVP; via Event Platform do **INTL** (pós-MVP). SALE **não** integra gateway de pagamento diretamente. |
| **PostgreSQL (`emp_<slug>`)** | persistência | Dados operacionais do tenant (pipeline, ofertas, compras, atribuição, LTV). |
| **Kafka / AWS MSK** | mensageria | Publica `oportunidade.*` / `compra.*` / `receita.*` / `ltv.*`; consome eventos LEAD e WRKS. |
| **Elasticsearch (`revenue-events`, `campaign-events`)** | busca/analytics | Indexa eventos de receita e de campanha (classe *fact*) para funil e relatórios. |
| **JRNY / COMM / INTL** | consumidores / pós-MVP | INTL indexa receita; JRNY/COMM reagem; (pós-MVP) SALE consome `routing.*`/sinais COMM como touchpoints. |

## 3. End-to-End Flows

### Golden path — Oportunidade → Compra → Receita atribuída (anchor: "Compra confirmada")

1. LEAD emite `journey-os.lead.qualificado`; SALE consome e cria/atualiza uma `oportunidade` no estágio inicial do pipeline (ou via `POST /api/v1/oportunidades`).
2. O closer (Lucas) move a oportunidade pelos estágios (`PATCH .../estagio`); SALE emite `oportunidade.estagio.alterado`.
3. Fechamento: a oportunidade é marcada **ganha** (`oportunidade.ganha`) ou **perdida** com motivo (`oportunidade.perdida`).
4. O checkout/gateway confirma o pedido → entra via `POST /api/v1/compras` (idempotente por `id_externo`); `application` resolve `EmpresaContextHolder`, cria a `compra` + `item_compra` (ofertas) e **reconhece a receita**.
5. Emite `journey-os.compra.confirmada` (**âncora**) e vincula a compra à `oportunidade` ganha (quando houver).
6. **Atribuição**: o domínio aplica o `modelo_atribuicao` (versão ativa) sobre os touchpoints do lead/jornada/campanha → distribui a receita; emite `journey-os.receita.atribuida`.
7. **LTV**: recalcula o LTV do contato (soma das compras confirmadas + breakdown); emite `journey-os.ltv.atualizado`.
8. Indexa os eventos de receita/campanha no Elastic (`revenue-events`, `campaign-events`).

### Fluxos alternativos

- **Compra sem oportunidade** (venda direta no checkout, sem CRM): `compra.confirmada` cria a receita e dispara atribuição/LTV mesmo sem `oportunidade` (atribuição usa origem do lead/contato).
- **Oportunidade perdida**: `oportunidade.perdida` com motivo; sem reconhecimento de receita; alimenta analytics de funil.
- **Reprocesso de pedido** (webhook duplicado): mesma `id_externo` → idempotência; nenhuma compra/receita nova.
- **Mudança de modelo de atribuição** (Marina troca `last-touch`→`linear`): nova versão ativa → re-atribuição (lote pequeno síncrono no MVP) das compras afetadas → `receita.atribuida`.
- **`empresa.provisionada` recebido**: seed de pipeline/estágios e ofertas default no novo `emp_<slug>`.
- **Estorno/cancelamento** (MVP básico): `compra` muda para `CANCELADA`/`ESTORNADA` → ajuste de receita e recálculo de LTV.

## 4. Internal Boundaries (camadas hexagonais)

```
com.journeyos.sale
├── api/                # controllers REST, DTOs (records), @RestControllerAdvice (ProblemDetail)
├── application/        # use cases (@Service, @Transactional, EmpresaContextHolder.require())
│   └── port/{in,out}   # in: casos de uso; out: repos, SaleSearchPort, SaleEventPublisherPort
├── domain/             # Oportunidade, Oferta, Compra, Atribuicao, Ltv (POJO puro)
│   └── service/        # PipelineService, AttributionEngine, LtvCalculator (zero Spring)
└── infrastructure/
    ├── config/         # DomainServiceConfig (@Bean dos domain services), Resilience4j, Feign
    ├── messaging/      # producer (oportunidade.*/compra.*/receita.*/ltv.*), consumer (lead.*, empresa.*)
    ├── persistence/    # entity/repository/adapter (PostgreSQL emp_<slug>)
    ├── search/         # adapter Elastic (revenue-events, campaign-events)
    └── security/       # JWT filter, EmpresaContextHolder, MDC
```

Regras de fronteira (ArchUnit): `domain` sem Spring/JPA; `@Transactional` só em `application.service`;
`api` não depende de `infrastructure`; `@FeignClient` só em `infrastructure.clients`. Ver `ADR-001`.

## 5. Cross-cutting Concerns

- **Security / multi-tenancy**: JWT validado (chave de WRKS); `EmpresaContextHolder` resolve o schema `emp_<slug>`; autorização por permissões `sale.<recurso>.<acao>` via `AccessDecision` (cache invalidado por `modelo.acesso.alterado`).
- **LGPD / privacidade**: `compra` carrega `base_legal`/consentimento do comprador; anonimização e expurgo; PII nunca em logs (MDC sem PII); eventos carregam IDs/valores, não PII sensível.
- **Observabilidade**: `correlationId` propagado (MDC); métricas de receita reconhecida, conversão por estágio, taxa de atribuição por modelo, latência de ingestão de compra; `audit-events` via eventos `compra.*`.
- **Idempotência**: ingestão de compra por (`id_externo` + `origem`); re-atribuição por (`compra_id` + `versao_modelo_atribuicao`).
- **Consistência financeira**: reconhecimento de receita e LTV em transação curta no `emp_<slug>`; estorno ajusta receita de forma rastreável (nunca exclui o histórico).

---

## Referências

- `01-architectural-vision.md` · `03-initial-domain-framing.md` · `05-persistence-model.md`
- ADRs: `adr/ADR-001..005`
- `docs/architecture/backend/standards/platform-patterns.md` (Kafka, Feign+Resilience4j, MDC)
- `docs/architecture/backend/services/lead-service/contracts/event-contracts.md` (eventos `lead.*` consumidos)
