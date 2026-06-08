# 06 — Risks, Gaps & Assumptions — LEAD (Lead Intelligence & Qualification)

> Tudo que pode invalidar a visão ou exige decisão antes/ao longo das specs.

## 1. Riscos

| # | Risco | Impacto | Mitigação |
|---|---|---|---|
| R1 | **Modelo das 6 dimensões mal calibrado** → score não correlaciona com conversão | Alto | Dimensões e pesos config-driven e versionados (`regra_qualificacao`); breakdown explicável permite ajuste por Marina; validar com dados reais no piloto. |
| R2 | **Dependência da TechLab AI** (latência/indisponibilidade) atrasa qualificação | Médio | Assist **opcional** com circuit breaker + fallback determinístico; SLA de timeout curto; flag `assist_ia` no breakdown. |
| R3 | **Dedup insuficiente** (mesmo lead em fontes diferentes) infla a base | Médio | Chave natural normalizada (email/telefone) + merge; dedup probabilística marcada como pós-MVP. |
| R4 | **PII vazando** em logs/eventos/Elastic (LGPD) | Alto | MDC sem PII; eventos carregam IDs, não PII sensível; índice `leads` com campos controlados; anonimização/expurgo suportados. |
| R5 | **Recálculo em massa** ao mudar regra trava o serviço | Médio | MVP: lote pequeno síncrono; volumes grandes → pipeline assíncrono (pós-MVP, registrado). |
| R6 | **Acoplamento a contratos a jusante** (JRNY/SALE/COMM ainda não existem) | Baixo | Integração só por eventos; contrato de evento estável e versionável; consumidores opcionais. |

## 2. Gaps Conhecidos

- **Definição final das 6 dimensões** e seus pesos/limiares — proposta no brief, a confirmar em `/be-architect-specs` (SPEC-03 Maturity Score 6D).
- **Contrato exato da capacidade `qualification` da TechLab AI** — snapshot em `integrations/techlab-ai/` ainda **vazio** (P3 bloqueado, aguarda primeiro commit upstream). DTOs não podem ser gerados até o sync.
- **Critérios de transição de estado** (`QUALIFICADO`/`NAO_QUALIFICADO`) — limiar configurável a definir.
- **Schema do índice Elastic `leads`** — campos indexados e mapeamentos a especificar.
- **Política de retenção/arquivamento** por empresa — a detalhar (MVP só marca expurgo).

## 3. Suposições a Validar

| # | Suposição | Como validar |
|---|---|---|
| A1 | As 6 dimensões `PERFIL/ENGAJAMENTO/INTENCAO/CAPACIDADE/URGENCIA/ADERENCIA` cobrem a qualificação do MVP | Revisão com growth (Marina) nas specs; ajustar nomes/escopo. |
| A2 | Kafka/AWS MSK é o event bus (não Artemis) | Confirmado por `project-context.json` + precedente WRKS; `ADR-003`. |
| A3 | LEAD escreve apenas no `emp_<slug>` (nada no global) | Alinhado a WRKS (escrita global exclusiva dele); ArchUnit/review. |
| A4 | Ingestão unitária + lote pequeno síncrono atende o volume do MVP | Estimar volume de captura por empresa no piloto. |
| A5 | TechLab AI `qualification` aceita texto livre e devolve contribuições por dimensão | Confirmar ao sincronizar `openapi.json` (sync-techlab-ai.py). |
| A6 | O índice `leads` (dimension) é suficiente para a fila priorizada sem store de leitura dedicado | Validar performance de consulta no piloto. |

## 4. Dependências Críticas

- **WRKS** disponível (AccessDecision/JWT + eventos `empresa.provisionada` / `modelo.acesso.alterado`) — **bloqueante** para autorização e seed por tenant.
- **MIG** com schema `emp_<slug>` provisionado — **bloqueante** para boot (`ddl-auto=validate`).
- **TechLab AI sync (P3)** — **bloqueante para a feature de assist IA** (geração de DTOs); a qualificação determinística não depende dele.
- **REG (Eureka)** — para descoberta do `wrks-service` via Feign.
- **Kafka/AWS MSK** e **Elasticsearch** disponíveis no ambiente local/dev.

---

## Referências

- `01-architectural-vision.md` (princípios) · `04-backend-architecture-direction.md` (integrações)
- ADRs: `adr/ADR-001..005`
- `docs/architecture/integrations/techlab-ai-integration.md`
- CLAUDE.md (regra: TechLab AI sync via `scripts/sync-techlab-ai.py`)
