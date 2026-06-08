# Hub Integration — intl-service (INTL)

> Integração de INTL com os serviços-hub internos do Journey OS (WRKS, ASST, MIG, REG).
> Comunicação inter-service via Feign (sync) + Kafka (async). EARS guide:
> `docs/architecture/backend/standards/ears-notation.md`.

## 1. WRKS (Workspace & Identity)

| Canal | Contrato | Uso |
|---|---|---|
| Feign `AccessEvaluateClient` (`@FeignClient(name="wrks-service")`) | `POST /api/v1/iam/access/evaluate` | Autorização de toda operação `intl.*`. |
| JWKS | `GET /api/v1/iam/.well-known/jwks.json` | Validação do JWT RS256. |
| Kafka | `journey-os.empresa.provisionada` | Seed da `base_conhecimento` + registro de índices. |
| Kafka | `journey-os.modelo.acesso.alterado` | Invalida cache local de AccessDecision. |

EARS:
- THE SYSTEM SHALL autorizar toda operação `intl.*` via `AccessEvaluateClient` antes de executá-la.
- WHEN `journey-os.modelo.acesso.alterado` é consumido, THE SYSTEM SHALL invalidar a entrada de cache da `empresa` afetada.

## 2. ASST (Asset Hub)

| Canal | Contrato | Uso |
|---|---|---|
| Feign `AssetQueryClient` (`@FeignClient(name="asst-service")`) | leitura de asset publicado | Buscar conteúdo do asset como fonte de conhecimento (opcional/enriquecimento). |
| Kafka | `journey-os.asset.versao.publicada` | Gatilho de ingestão de nó de conhecimento. |

EARS:
- WHEN `journey-os.asset.versao.publicada` é consumido, THE SYSTEM SHALL ingerir o conteúdo publicado como nó `fonte=ASSET` (referência `assetId:versao`).
- WHERE o evento não traz o conteúdo completo, THE SYSTEM SHALL buscá-lo via `AssetQueryClient`.

## 3. MIG (Migrations)

| Canal | Contrato | Uso |
|---|---|---|
| Pré-condição | schema `emp_<slug>` preparado | INTL roda `ddl-auto=validate`. |

EARS:
- THE SYSTEM SHALL assumir o schema `emp_<slug>` já migrado por MIG (não cria schema em runtime).

## 4. REG (Service Registry)

| Canal | Contrato | Uso |
|---|---|---|
| Eureka | registro/descoberta | Resolução dos clientes Feign (`wrks-service`, `asst-service`). |

## 5. Elasticsearch (plataforma de dados)

| Canal | Contrato | Uso |
|---|---|---|
| `elastic-client-lib` `SearchPort` | recuperação RAG + analítica cross-index | leitura, sempre filtrando `empresa`. |
| `elastic-client-lib` `IndexPort` | projeção própria (`ai-copilot-events`, `knowledge-nodes`) + DLQ | escrita com bloco de rastreabilidade. |

EARS:
- THE SYSTEM SHALL incluir o bloco de rastreabilidade de 8 campos + `empresa` em todo documento projetado.
- IF um documento viola o contrato de rastreabilidade, THEN THE SYSTEM SHALL roteá-lo para `journey-os_dlq` (`parse_status=error`).
