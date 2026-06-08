# 03 — Domain Framing (Frontend) — LEAD

> Linguagem ubíqua (espelho do BE), View Models, UI Events, transições de estado e invariantes
> client-side. **Não redefinir o domínio** — referência: `_brief.md` + BE `03-initial-domain-framing.md`
> + `contracts/api-contract.md`.

## 1. Ubiquitous Language (espelho do BE)

| Termo | Significado (FE) |
|---|---|
| **Lead** | Pessoa/contato único por `empresa`, com perfil, score e estado de qualificação. |
| **Perfil (`perfil_lead`)** | Conjunto de atributos tipados do lead, com **origem** (`MANUAL`/`SURVEY`/`CAPTURA`) e **base legal** (LGPD). |
| **Maturity Score (6D)** | Índice agregado + **breakdown** nas dimensões `PERFIL`, `ENGAJAMENTO`, `INTENCAO`, `CAPACIDADE`, `URGENCIA`, `ADERENCIA`. Sempre com `versaoRegra` e flag `assistIa`. |
| **Estado de qualificação** | `EM_QUALIFICACAO` · `QUALIFICADO` · `ANONIMIZADO` (terminal LGPD). |
| **Segmento** | Agrupamento dinâmico definido por **predicado** sobre perfil+score; membership reavaliada pelo BE. |
| **Survey / Pergunta / Resposta** | Questionário versionado; respostas viram atributos `origem=SURVEY` e disparam recálculo. |
| **Regra de qualificação (`regra_qualificacao`)** | Configuração **versionada**; mapeia sinais → contribuição por dimensão. Apenas uma **ativa** por vez. |
| **Base legal** | Fundamento LGPD do tratamento do dado (ex.: `CONSENTIMENTO`, `LEGITIMO_INTERESSE`). |
| **Assist IA (`assistIa`)** | Indica se o score usou a interpretação opcional da TechLab AI (BE) ou foi puramente determinístico. |

## 2. View Models (rascunho)

```ts
// Fila (feature-lead-list)
type LeadRowVM = {
  leadId: string;
  nome: string;                 // suprimido se ANONIMIZADO
  scoreTotal: number;           // 0..100
  faixa: 'FRIO' | 'MORNO' | 'QUENTE';
  estado: 'EM_QUALIFICACAO' | 'QUALIFICADO' | 'ANONIMIZADO';
  segmentos: string[];
  assistIa: boolean;
  atualizadoEm: string;
};

// Detalhe (feature-lead-detail)
type LeadDetailVM = {
  leadId: string;
  perfil: { nome?: string; email?: string; telefone?: string; atributos: AtributoVM[]; baseLegal: string };
  estado: 'EM_QUALIFICACAO' | 'QUALIFICADO' | 'ANONIMIZADO';
  score: MaturityScoreVM;
  acoesDisponiveis: LeadAcao[];   // derivado de estado + permissões
};
type AtributoVM = { chave: string; valor: string; origem: 'MANUAL' | 'SURVEY' | 'CAPTURA' };

// Maturity Score (feature-maturity-score / ui/score-radar)
type MaturityScoreVM = {
  total: number;                        // 0..100
  dimensoes: DimensaoVM[];              // exatamente 6
  versaoRegra: number;
  assistIa: boolean;                    // false => badge "score determinístico"
  calculadoEm: string;
};
type DimensaoVM = { dimensao: 'PERFIL'|'ENGAJAMENTO'|'INTENCAO'|'CAPACIDADE'|'URGENCIA'|'ADERENCIA'; valor: number; peso: number };

// Distribuição (feature-maturity-score dashboard)
type MaturityDistributionVM = {
  histograma: { faixa: string; quantidade: number }[];
  saudePorDimensao: { dimensao: string; media: number }[];
  pctComAssistIa: number;
};

// Segmento (feature-segmentation)
type SegmentoVM = { id: string; nome: string; predicado: string; quantidadeLeads: number; ativo: boolean };

// Survey (feature-survey)
type SurveyVM = { id: string; titulo: string; versao: number; perguntas: PerguntaVM[] };
type PerguntaVM = { id: string; texto: string; tipo: 'TEXTO'|'ESCOLHA'|'NUMERO'|'BOOLEANO'; mapeiaAtributo: string };

// Regra (feature-qualification-rules)
type RegraVersaoVM = { versao: number; ativa: boolean; criadaEm: string; resumoDimensoes: string };
```

## 3. UI Events

- `FilaFiltrada(segmento?, dimensao?, estado?, busca?)` → recarrega a fila.
- `LeadSelecionado(leadId)` → navega ao detalhe; carrega perfil + breakdown.
- `PerfilEditado(leadId, atributos)` → `PUT /leads/{id}` → recálculo no BE.
- `RequalificarSolicitado(leadId)` → `POST /leads/{id}/qualify` → atualiza score.
- `LeadAnonimizado(leadId)` / `LeadExpurgado(leadId)` → ações LGPD (confirmação obrigatória).
- `SegmentoSalvo(segmento)` / `SegmentoExcluido(id)` → CRUD de segmento.
- `RespostasSurveyEnviadas(leadId, surveyId, respostas)` → atualiza perfil.
- `VersaoRegraCriada(payload)` / `VersaoRegraAtivada(versao)` → governança de regra.

## 4. State Transitions (UI)

```
Fila / Detalhe (carregamento):   idle → loading → success | empty | error
Requalificar:                    ready → submitting → success(score atualizado) | blocked(sem-regra-ativa) | error
Edição de perfil:                view → editing → saving → success | error   (bloqueado se ANONIMIZADO)
Ativação de regra:               inativa → activating → ativa (anterior desativada) | error(404 regra-nao-encontrada)
Segmento (prévia):               editing-predicado → previewing(contagem) → saved | invalid(422 predicado-invalido)
Assist IA (badge):               assistIa=true → "IA ✓"  |  assistIa=false → "score determinístico"
```

## 5. Invariants (client-side)

- O Maturity Score **nunca** é renderizado sem o breakdown 6D + `versaoRegra` + badge de `assistIa`.
- As 6 dimensões são exibidas **sempre as seis** (faltando valor → 0 com indicação), nunca um subconjunto silencioso.
- Faixa de score **não depende só de cor** — sempre rótulo textual + número (acessibilidade).
- Ações LGPD (`anonimizar`/`expurgar`) exigem **confirmação explícita** e só aparecem com a permissão correspondente.
- Lead `ANONIMIZADO` → edição de perfil e `qualify` **desabilitados** na UI (espelha `409 lead.lead.anonimizado`).
- Predicado de segmento é validado client-side (forma) antes do `POST`; o veredito final é do BE
  (`422 lead.segment.predicado-invalido`).
- Base legal é **obrigatória** em qualquer criação/edição que a exponha (espelha `422 lead.lead.base-legal-invalida`).
- Troca de empresa limpa toda a fila/seleção em tela antes de carregar dados da nova empresa.

---

## Referências

- BE: `docs/architecture/backend/services/lead-service/03-initial-domain-framing.md` + `contracts/api-contract.md`
- `05-state-and-data-flow.md` (data flow detalhado) · `ADR-005` (visualização do Maturity Score)
- `docs/architecture/frontend/standards/access-layer-contracts.md`
