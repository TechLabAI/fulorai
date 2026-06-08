# 03 — Initial Domain Framing — INTL

> Rascunho inicial do domínio. Refinado por `/be-architect-specs` (contracts/data-model).

## 1. Ubiquitous Language

| Termo (pt-BR) | Definição |
|---|---|
| **Copiloto** | Assistente conversacional que responde perguntas fundamentadas sobre a `empresa`. |
| **Conversa** (`ConversaCopiloto`) | Sessão de diálogo do copiloto, com sequência de mensagens. |
| **Mensagem** (`MensagemCopiloto`) | Turno da conversa (`papel` = USUARIO ou COPILOTO). |
| **Citação** (`Citacao`) | Referência verificável (id de documento Elastic + trecho) que fundamenta a resposta. |
| **Fundamentação** | Propriedade de uma resposta de estar ancorada em evidência citável. |
| **Nó de Conhecimento** (`NoConhecimento`) | Unidade curada de conhecimento da `empresa` (texto + metadados + embedding). |
| **Base de Conhecimento** (`BaseConhecimento`) | Conjunto de nós de uma `empresa`; alimenta o RAG. |
| **Fonte de Conhecimento** (`FonteConhecimento`) | Origem de um nó (MANUAL, ASSET, …). |
| **Recuperação (RAG)** | Busca de evidência no Elastic que precede a composição da resposta. |
| **Evento Indexado** (`EventoIndexado`) | Registro (ledger) de uma projeção feita por INTL no Elastic. |
| **Registro de Índice** (`RegistroIndice`) | Metadado de governança de um índice da plataforma (classe, ILM, mapeamento). |
| **Contrato de Rastreabilidade** | Bloco obrigatório de 8 campos em todo documento indexado (D-269). |
| **DLQ** | Índice `journey-os_dlq` para documentos que violam o contrato ou falham a indexação. |
| **Degradada / `nao_fundamentada`** | Estado de resposta sem síntese de IA ou sem citação fundamentada. |

## 2. Aggregates and Entities (rascunho)

- **`ConversaCopiloto`** (aggregate root) — `id`, `empresa`, `usuario_ref`, `titulo`, `estado`,
  `criada_em`. Contém **`MensagemCopiloto`** (entity): `id`, `papel`, `conteudo`, `status`,
  `modelo`, `custo_tokens`, `latencia_ms`, `criada_em`, e **`Citacao`** (VO): `documento_id`,
  `indice`, `trecho`, `score`.
- **`BaseConhecimento`** (aggregate root, 1:1 com `empresa`) — contém **`NoConhecimento`** (entity):
  `id`, `fonte` (`FonteConhecimento` VO: `tipo`, `referencia`), `titulo`, `conteudo`, `tags[]`,
  `embedding_ref`, `status`, `versao`, `atualizado_em`.
- **`EventoIndexado`** (entity/ledger, append-only) — `evento_id`, `tipo`, `indice_alvo`,
  `status` (INDEXADO|DLQ), `indexado_em`. Suporta idempotência/replay e auditoria.
- **`RegistroIndice`** (entity, governança — possivelmente `journeyos_global`) — `nome`, `classe`
  (dimension|fact), `dono` (módulo), `ilm`, `ativo`.

## 3. Domain Events (inicial)

**Produzidos (Kafka):**
- `journey-os.copilot.resposta.gerada` (**âncora**) — após gerar resposta (fundamentada ou
  degradada). Projetado em `ai-copilot-events`.

*(Pós-MVP: `journey-os.insight.gerado`, `journey-os.no.conhecimento.indexado`.)*

**Consumidos (Kafka):**
- `journey-os.asset.versao.publicada` (ASST) → ingere/atualiza nó de conhecimento.
- `journey-os.empresa.provisionada` (WRKS) → seed da base + registro de índices por tenant.
- `journey-os.modelo.acesso.alterado` (WRKS) → invalida cache AccessDecision.

## 4. State Transitions (alto nível)

```
ConversaCopiloto:   ABERTA ──(pergunta)──► PROCESSANDO ──► RESPONDIDA
                                                  │
                                                  ├─(IA off)──► DEGRADADA
                                                  └─(erro)────► ERRO
MensagemCopiloto:   PENDENTE ──► RESPONDIDA | DEGRADADA | nao_fundamentada | ERRO
NoConhecimento:     RASCUNHO ──(embed+index)──► INDEXADO ──(reembedding)──► INDEXADO
                                     │                                         │
                                     └──────────────► ARQUIVADO ◄─────────────┘
EventoIndexado:     RECEBIDO ──► INDEXADO | DLQ
```

## 5. Invariants

- **INV-1 (rastreabilidade):** todo documento indexado por INTL carrega o bloco de 8 campos
  (D-269) + `empresa`; ausência → DLQ (`parse_status=error`), nunca indexação parcial silenciosa.
- **INV-2 (fundamentação):** resposta do copiloto referencia evidência recuperável; resposta sem
  citação fundamentada é marcada `nao_fundamentada` — nunca apresentada como fato confirmado.
- **INV-3 (sem IA direta):** nenhuma chamada a provedor de IA fora da TechLab AI.
- **INV-4 (idempotência):** doc-id determinístico; reprocessar o mesmo evento/nó não duplica.
- **INV-5 (isolamento de tenant):** escrita PG só no `emp_<slug>` resolvido; **toda** consulta
  Elastic filtra `empresa`. Citação nunca cruza tenant.
- **INV-6 (descentralização):** INTL não escreve nos *facts* de outros módulos
  (`journey-events`/`routing-decisions`/`communication-events`/`revenue-events`/`campaign-events`);
  apenas lê. Escreve só `ai-copilot-events` e `knowledge-nodes`.
