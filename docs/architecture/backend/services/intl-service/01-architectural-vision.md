# 01 — Architectural Vision — INTL (Intelligence & Platform)

> Serviço: `intl-service` · Pacote: `com.journeyos.intl` · Porta: `8087` · Type: `standard`

## 1. Intent

INTL é a **camada de inteligência e plataforma** do Journey OS. Entrega duas capacidades
acopladas a um único serviço:

1. **AI Copilot + Base de Conhecimento** — um copiloto conversacional que responde, em
   linguagem natural, perguntas **fundamentadas e citadas** sobre os dados de uma `empresa`,
   ancorado numa Base de Conhecimento curada e em recuperação (RAG) sobre o Elasticsearch.
2. **Governança da plataforma de dados Elastic + leitura analítica** — INTL é o dono do
   **contrato de dados** (rastreabilidade, DLQ, registro de índices, ILM) que todos os módulos
   produtores respeitam ao indexar, e oferece a **superfície de leitura analítica** cross-index
   (funil, ROI, jornada) consolidada por `empresa`.

INTL **não** reprocessa os *facts* dos outros módulos (cada produtor projeta os seus) e **não**
chama provedores de IA diretamente (sempre via TechLab AI).

## 2. Problem Statement

Uma operação de educação digital gera sinais ricos em todos os módulos — leads qualificados,
jornadas, mensagens, vendas — mas (a) **não consegue perguntar** ao próprio sistema o que está
acontecendo sem montar relatórios manuais, e (b) a leitura analítica está **fragmentada** por
vários índices Elastic, cada um governado de forma diferente, sem um contrato de rastreabilidade
único. Falta uma camada que transforme dados dispersos em **respostas auditáveis** e em
**analítica consolidada e confiável**, sem cair na armadilha de uma "IA caixa-preta" que alucina
fatos. INTL resolve isso com RAG fundamentado (citações verificáveis), governança de dados única
e leitura analítica por `empresa`.

## 3. Personas

| Papel | Persona | Uso de INTL |
|---|---|---|
| **Principal** | `INFOPRODUTOR` (Rafael) | Pergunta ao Copilot sobre o negócio; lê analítica consolidada (faturamento, funil, ROI). |
| **Secundária** | `HEAD_GROWTH` (Marina) | Curadoria da Base de Conhecimento; analítica por origem/campanha; valida fundamentação das respostas. |
| **Terciária** | `SDR` (Lucas) | Copilot para resumos rápidos de contexto de lead/funil antes de uma call. |
| **Máquina** | ASST | Emite `asset.versao.publicada` → INTL ingere o conteúdo como nó de conhecimento. |
| **Máquina** | WRKS | Emite `empresa.provisionada` (seed da base/registro de índices) e `modelo.acesso.alterado` (cache). |
| **Máquina** | JRNY / COMM / SALE | Projetam seus próprios *facts* respeitando o **contrato de dados governado por INTL**. |

## 4. MVP Scope (in)

1. **AI Copilot (read-only, síncrono)** — `/api/v1/copilot/**`: pergunta + contexto `empresa` →
   RAG (recuperação Elastic → composição TechLab AI) → resposta **com citações**; persiste
   `conversa_copiloto` + `mensagem_copiloto`; emite `journey-os.copilot.resposta.gerada`.
2. **Base de Conhecimento** — `/api/v1/knowledge/**`: CRUD/curadoria de `no_conhecimento`
   (canônico em PostgreSQL, indexado no índice Elastic `knowledge-nodes` *dimension*); ingestão
   manual e a partir de `asset.versao.publicada`.
3. **Governança da plataforma Elastic** — dono do contrato de rastreabilidade (8 campos — D-269),
   registro de índices + mapeamentos/ILM, roteamento DLQ (`journey-os_dlq`), e projeção dos
   índices **próprios** (`ai-copilot-events`, `knowledge-nodes`).
4. **Leitura analítica cross-index** — `/api/v1/analytics/**`: agrega *facts* já projetados pelos
   módulos produtores (funil/ROI/jornada), sempre filtrando por `empresa`.
5. **Degradação graciosa** — TechLab AI indisponível → modo recuperação-apenas; a resposta é
   marcada `nao_fundamentada`/degradada, nunca alucina fato como fundamentado.

## 5. Out of Scope (MVP)

- **Reindexação dos *facts* de outros módulos** — cada produtor (JRNY/COMM/SALE) projeta os seus.
- **Ingestão de observabilidade** (`app-logs`/`traces`/`metrics`/`integration-logs`) — INTL declara
  os índices/ILM; a ingestão é de agentes de infra/APM (Filebeat/OTel), não de código de domínio.
- **Integration Hub externo** (conectores/webhooks de 3º — Hotmart/gateways) — pós-MVP.
- **Copilot com ações/automações** (escrita de volta, agentes que executam) — MVP é leitura.
- **Analytics preditivo/ML** (forecast, alerting, dashboard builder) — pós-MVP (`analytics`).
- **Fine-tuning de embeddings/reranking** além do que a TechLab AI provê.

## 6. Architectural Principles

- **Fundamentação acima de fluência** — toda resposta cita evidência recuperável; sem citação →
  marcada `nao_fundamentada`. Nunca apresentar fato alucinado como fundamentado.
- **IA sempre via TechLab AI** — proibido chamar provedor de IA direto (RULE do monorepo).
- **Plataforma de dados descentralizada na escrita, centralizada no contrato** — cada módulo
  escreve seus *facts*; INTL governa o contrato único (rastreabilidade, DLQ, ILM, registro).
- **Isolamento de tenant inviolável** — PG por schema; Elastic por filtro `empresa` obrigatório.
- **Idempotência e auditabilidade** (D-269) — doc-id determinístico; bloco de rastreabilidade
  obrigatório; nada é indexado sem trilha.
- **Degradação graciosa** — a falha da IA reduz a qualidade da resposta, nunca derruba o serviço.
- **Hexagonal estrito** — domínio puro; Elastic/TechLab AI/Kafka atrás de portas.

## 7. Success Signals

- Rafael obtém resposta fundamentada (≥ 1 citação verificável) a uma pergunta de negócio em
  segundos, sem montar relatório.
- 100% dos documentos indexados por INTL carregam o bloco de rastreabilidade de 8 campos;
  documentos inválidos vão ao DLQ (0 indexações silenciosas inválidas).
- Toda consulta analítica/recuperação é filtrada por `empresa` (0 vazamentos cross-tenant).
- Indisponibilidade da TechLab AI não derruba o Copilot — responde em modo degradado e o sinaliza.
- Reprocessar o mesmo evento/nó não duplica documento no Elastic (idempotência verificada).
