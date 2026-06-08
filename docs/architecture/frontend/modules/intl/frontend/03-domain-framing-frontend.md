# 03 — Domain Framing (Frontend) — INTL

> Espelho do domínio do BE (`intl-service/03-initial-domain-framing.md`). Não redefine a linguagem
> ubíqua — referencia o BO e recorta os **View Models**, **eventos de UI** e **transições** do FE.

## 1. Ubiquitous Language (espelho do BE — não redefinir)

| Termo | Papel no FE |
|---|---|
| **Copiloto** | Superfície de chat onde o usuário pergunta e recebe resposta fundamentada. |
| **Conversa** (`ConversaCopiloto`) | Item da lista lateral; agrupa mensagens; tem `estado`. |
| **Mensagem** (`MensagemCopiloto`) | Bolha de chat (`papel` = USUARIO \| COPILOTO). |
| **Citação** (`Citacao`) | Chip clicável (`documentoId`, `indice`, `trecho`, `score`) que fundamenta a resposta. |
| **Fundamentação** | Propriedade visual: resposta com ≥ 1 citação → renderizada como fato; sem → sinalizada. |
| **Nó de Conhecimento** (`NoConhecimento`) | Linha da tabela / card editável da Base de Conhecimento. |
| **Base de Conhecimento** | A coleção de nós da empresa ativa (escopo da lista/busca). |
| **Fonte** (`FonteConhecimento`) | Origem do nó (`MANUAL` \| `ASSET`) — badge na linha. |
| **Status de resposta** | `RESPONDIDA` \| `NAO_FUNDAMENTADA` \| `DEGRADADA` — dirige o tratamento visual. |
| **Funil / Uso do Copiloto** | View Models de Analytics (read-only). |

Definições canônicas: `docs/architecture/backend/services/intl-service/03-initial-domain-framing.md`.

## 2. View Models (rascunho por tela)

```ts
// feature-copilot — lista lateral
ConversaListItemVM { id; titulo; estado: 'ABERTA'|'PROCESSANDO'|'RESPONDIDA'|'ERRO'; atualizadaEm }

// feature-copilot — chat
MensagemVM {
  id; papel: 'USUARIO'|'COPILOTO'; conteudo;
  status?: 'RESPONDIDA'|'NAO_FUNDAMENTADA'|'DEGRADADA'|'PENDENTE'|'ERRO';
  citacoes: CitacaoVM[]; modelo?; custoTokens?; latenciaMs?; criadaEm;
}
CitacaoVM { documentoId; indice; trecho; score }

// feature-knowledge — lista
NoConhecimentoRowVM { id; titulo; tags: string[]; fonte: 'MANUAL'|'ASSET'; status: 'RASCUNHO'|'INDEXADO'|'ARQUIVADO'; versao; atualizadoEm }
// feature-knowledge — form
NoConhecimentoFormVM { id?; titulo; conteudo; tags: string[]; fonte: { tipo: 'MANUAL'; referencia?: string } }

// feature-analytics
FunilVM { periodo; etapas: { nome; total }[] }
CopilotUsageVM { totalRespostas; custoTokens; taxaFundamentadas; taxaDegradadas }
```

## 3. UI Events (disparados pelo usuário)

- `abrirConversa()` / `selecionarConversa(id)` / `novaConversa(titulo?)`.
- `enviarPergunta(conversaId, texto, topK?)` → otimista: insere `MensagemVM(USUARIO)` + bolha
  `COPILOTO` em `PENDENTE`.
- `cancelarPergunta()` → aborta a requisição in-flight.
- `abrirCitacao(citacao)` → navega/abre o documento-fonte (deep-link / painel lateral).
- Knowledge: `buscarNos(filtros)`, `criarNo(form)`, `editarNo(id, form)`, `indexarNo(id)`,
  `arquivarNo(id)`.
- Analytics: `mudarPeriodo(periodo)`, `mudarGranularidade(g)`.

## 4. State Transitions (nível de UI)

```
Pergunta (bolha COPILOTO):
  PENDENTE ──(200 RESPONDIDA)──► RESPONDIDA
     │     ──(200 NAO_FUNDAMENTADA)──► NAO_FUNDAMENTADA
     │     ──(200 DEGRADADA)──────────► DEGRADADA
     │     ──(cancelar)──────────────► (removida, volta a idle)
     └─────(erro de transporte / 4xx)─► ERRO

Nó de conhecimento (form/linha):
  idle → salvando → RASCUNHO
  RASCUNHO ──(indexar)──► indexando ──(202)──► INDEXADO
                                  └──(503)──► RASCUNHO (retry)
  INDEXADO/RASCUNHO ──(arquivar)──► ARQUIVADO

Dashboard analytics:  idle → loading → success | empty | error
```

## 5. Invariants (client-side)

- **INV-FE-1 (fundamentação visual):** bolha `RESPONDIDA` SÓ renderiza chips de citação reais
  recebidos do BE; `NAO_FUNDAMENTADA`/`DEGRADADA` **nunca** renderizam citação fabricada.
- **INV-FE-2 (pergunta não-vazia):** `enviarPergunta` exige `texto` não-vazio (trim) e bloqueia
  envio concorrente enquanto há bolha `PENDENTE` na conversa.
- **INV-FE-3 (form de nó):** `titulo` e `conteudo` obrigatórios; `tags` opcional; `fonte.tipo` fixo
  em `MANUAL` na criação manual (ASSET vem do BE via evento).
- **INV-FE-4 (isolamento):** todo VM é derivado de respostas escopadas por `empresa`; trocar de
  empresa invalida conversa/listas/dashboards correntes.
- **INV-FE-5 (degradação não é erro):** `503` no Copilot nunca ocorre (BE degrada para `200`); `503`
  na indexação é tratado como **retry**, não como falha terminal.
- **INV-FE-6 (read-only analytics):** telas de Analytics não expõem nenhuma ação de escrita.

---

## Referências

- BE: `docs/architecture/backend/services/intl-service/03-initial-domain-framing.md`
- API: `docs/architecture/backend/services/intl-service/contracts/api-contract.md`
- `05-state-and-data-flow.md` (data flow detalhado)
