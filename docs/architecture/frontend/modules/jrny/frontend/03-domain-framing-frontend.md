# 03 — Domain Framing (Frontend) — JRNY (Journey & Routing)

> Linguagem ubíqua **espelhada do BE** (não redefinir). View Models, eventos de UI, transições de
> estado e invariantes client-side. Fonte: `jrny-service/_brief.md`, `03-initial-domain-framing.md`,
> `contracts/api-contract.md`.

## 1. Ubiquitous Language (espelho do BE)

| Termo | Significado (FE) |
|---|---|
| **Jornada** (`jornada`) | Agregado: sequência de estágios ordenados, com `estadoJornada` (`RASCUNHO`/`PUBLICADA`/`ARQUIVADA`) e `versao`. |
| **Estágio** (`estagio`) | Passo tipado da jornada (`CAPTURA`, `NUTRICAO`, `QUALIFICACAO`, `OFERTA`, `FECHAMENTO`, `POS_VENDA`), com `ordem`, `nome`, `assetRefId`, `terminal`, `config`. |
| **Regra de roteamento** (`regra_roteamento`) | Regra **versionada**: `condicao` (sobre score/segmento/atributo), `estagioOrigemId`→`estagioDestinoId`, `prioridade`, `ativa`, `versao`. |
| **Inscrição de jornada** (`inscricao_jornada`) | Estado corrente do lead numa jornada: `estagioCorrenteId`, `jornadaVersao`, `estado`, `entrouEm`. |
| **Decisão de roteamento** (`decisao_roteamento`) | Registro **imutável**: `gatilho`, `regraId`, `assistIa`, `resultado`, `estagioAlvoId`, `motivo`, `decididoEm`. |
| **Assist IA** (`assistIa`) | Flag: a decisão usou a recomendação da TechLab AI (`orchestration`) ou foi puramente determinística. |
| **Gatilho** (`gatilho`) | Evento que originou a decisão (ex.: `lead.qualificado`, `score.atualizado`, `segmento.alterado`). |
| **Resultado** (`resultado`) | Desfecho da decisão: roteado, `SEM_MUDANCA`, `NAO_ROTEADO`. |

> JRNY **não** redefine `lead`/`score`/`segmento` (domínio de LEAD) nem `asset` (domínio de ASST) —
> apenas os **referencia** por id.

## 2. View Models (rascunho por tela)

```
JourneyListItemVm   { id, nome, descricao, estadoJornada, versao, qtdEstagios, atualizadoEm, podeEditar }
JourneyBuilderVm    { id, nome, descricao, estadoJornada, versao, editavel, estagios: StageItemVm[],
                      acoesDisponiveis: ('publicar'|'arquivar'|'nova-versao'|'add-estagio')[] }
StageItemVm         { id, ordem, tipoEstagio, nome, assetRefId, assetRefLabel?, terminal, temRegrasSaindo }
StageEditorVm       { id?, ordem, tipoEstagio, nome, assetRefId, terminal, config, erros: FieldError[] }
RoutingRuleVm       { id, jornadaId, estagioOrigemNome?, estagioDestinoNome, condicaoResumo, prioridade,
                      versao, ativa }
RuleEditorVm        { id?, jornadaId, estagioOrigemId?, estagioDestinoId, condicao, prioridade, erros }
LeadJourneyStateVm  { leadId, jornadaNome, jornadaVersao, estagioCorrenteNome, tipoEstagioCorrente,
                      estado, entrouEm, semInscricao: boolean }
DecisionItemVm      { id, gatilho, regraVersaoLabel, resultado, estagioAlvoNome, assistIa, motivo, decididoEm }
JourneyAnalyticsVm  { jornadaId, funil: { tipoEstagio, qtdLeads }[], taxaAssistIa, totalDecisoes }
```

Cada VM é **derivado** (via `computed()`) das respostas do BE — a UI não expõe entidades cruas.
`podeEditar`/`editavel` derivam de `estadoJornada === 'RASCUNHO'` **e** da permissão.

## 3. UI Events (disparados pelo usuário)

- `criarJornada(nome, descricao)` → `POST /journeys`
- `abrirBuilder(id)` / `editarMetadados(id, patch)` → `PATCH /journeys/{id}`
- `adicionarEstagio(id, stage)` / `editarEstagio(id, estagioId, patch)` / `reordenarEstagios(id, ordem[])`
- `publicarJornada(id)` → `POST /journeys/{id}/publicar`
- `arquivarJornada(id)` → `POST /journeys/{id}/arquivar`
- `criarNovaVersao(id)` → `POST /journeys/{id}/nova-versao`
- `criarRegra(rule)` / `editarRegra(ruleId, patch)` → `POST|PATCH /routing/rules`
- `buscarEstadoLead(leadId)` → `GET /routing/leads/{leadId}/journey`
- `carregarDecisoes(leadId, page)` → `GET /routing/leads/{leadId}/decisions`
- `trocarEmpresa()` → invalida estado em tela (efeito da Access Layer)

## 4. State Transitions (UI)

```
Jornada (máquina de estados — espelha o BE):
  RASCUNHO --publicar(≥1 estágio)--> PUBLICADA --nova-versao--> (novo RASCUNHO v+1)
  RASCUNHO --arquivar--> ARQUIVADA
  PUBLICADA --arquivar--> ARQUIVADA
  (PUBLICADA/ARQUIVADA = read-only no builder)

Carregamento de qualquer tela:
  idle -> loading -> success | empty | error
  (empty: jornada sem estágio, lead sem inscrição, sem decisões)

Decisão (render):
  resultado ∈ { roteado, SEM_MUDANCA, NAO_ROTEADO }
  assistIa ∈ { true -> badge "IA ✓", false -> badge neutro "determinístico" }
```

## 5. Invariants (client-side)

- **Edição só em RASCUNHO** — toda UI de edição de jornada/estágio/regra é desabilitada se
  `estadoJornada !== 'RASCUNHO'` (a verdade é do BE; o FE previne a ação e oferece "nova versão").
- **Publicar exige ≥ 1 estágio** — botão publicar desabilitado/avisado sem estágios.
- **`tipoEstagio`** ∈ enum fechado (`CAPTURA`…`POS_VENDA`); seleção por enum, nunca texto livre.
- **`ordem` única** por jornada — validação client-side antes do submit (espelha `409 ordem-duplicada`).
- **Regra: estágio-destino pertence à jornada** — seletor restrito aos estágios da jornada.
- **`prioridade`** numérica; ordenação visível.
- **Decisão é read-only** — nenhuma UI muta `decisao_roteamento` (imutável por construção).
- **Decisão sempre explicável** — render proíbe mostrar `estagioAlvo` sem `gatilho` + `regra` + `assistIa` + `motivo`.
- **IA-off não é erro** — `assistIa=false` é badge neutro, jamais estado de erro.

---

## Referências

- `01-architectural-vision.md` · `02-architecture-blueprint.md` · `05-state-and-data-flow.md`
- BE: `jrny-service/03-initial-domain-framing.md` · `contracts/{api-contract,data-model}.md`
