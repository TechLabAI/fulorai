# ADR-005 — Visualização explicável do Maturity Score (6D) — LEAD

- **Status:** accepted
- **Específico do LEAD** (decisão crítica extraída do brief)

## Contexto

O coração do LEAD é o **Maturity Score (6D)** — um índice agregado com breakdown nas dimensões
`PERFIL`, `ENGAJAMENTO`, `INTENCAO`, `CAPACIDADE`, `URGENCIA`, `ADERENCIA`. O brief BE é categórico:
o score é **determinístico e explicável**, com **assist opcional** da TechLab AI (capacidade
`qualification`) que **degrada com graça** para o resultado determinístico em falha
(`lead.ia.indisponivel` **não** é erro HTTP). O risco-chave de produto (R1) é a UI transformar o score
numa **caixa-preta** ou apresentar a degradação do assist como "erro"/"score pior".

## Decisão

A UI do LEAD trata o Maturity Score como um **artefato explicável de primeira classe**:

1. **Nunca exibir o número agregado sozinho.** Toda apresentação do score acompanha:
   - o **breakdown das 6 dimensões** (componente `score-radar` + `dimension-bar` em `libs/lead/ui`),
     sempre as **seis** dimensões (faltante → 0 com indicação);
   - a **versão de regra** (`versaoRegra`) que produziu o score;
   - o **badge `assistIa`**: `IA ✓` quando houve assist, **"score determinístico"** quando não houve.
2. **Degradação graciosa, não erro.** `assistIa=false` (inclui o caso `lead.ia.indisponivel`) é
   renderizado com um badge **neutro**, jamais como toast/estado de erro. A funcionalidade permanece
   intacta (o score determinístico é a fonte da verdade).
3. **Acessibilidade obrigatória.** A faixa do score (`FRIO/MORNO/QUENTE`) nunca depende só de cor —
   sempre rótulo textual + número; o radar tem tabela alternativa para leitores de tela; contraste AA.
4. **Dashboard de distribuição** (`feature-maturity-score`) reusa o `score-radar` e adiciona
   histograma do agregado + saúde por dimensão + `% com assist IA`, para a persona `HEAD_GROWTH`
   monitorar a base.
5. **Componentes de visualização leves.** Preferir SVG/CSS próprio (`libs/lead/ui`) a libs de chart
   pesadas; se uma lib for necessária, carregar por import dinâmico (orçamento de bundle no SPEC).

## Alternativas consideradas

- **Mostrar só o número agregado** (com drill-down opcional) — rejeitada: viola o princípio "score
  explicável" e o success signal do SDR entender *por quê*.
- **Tratar IA-off como estado de erro/aviso forte** — rejeitada: contradiz o contrato BE (não é erro)
  e mina a confiança.
- **Lib de chart pesada (ex.: full charting framework)** — adiada: custo de bundle desproporcional ao
  MVP; reavaliar se o dashboard crescer.

## Consequências

**Positivas:** transparência e confiança no score; resiliência à queda da IA sem ruído; acessível;
reuso do radar entre detalhe e dashboard. **Negativas:** mais componentes de UI a construir/testar
(`score-radar`, `dimension-bar`, `maturity-distribution-chart`) e disciplina de a11y; orçamento de
bundle a monitorar.

## Referências

- `_brief.md` (itens 7, 8 + notas) · `01-architectural-vision.md` (§6, §7) · `03-domain-framing-frontend.md`
- BE: `lead-service/adr/ADR-005-maturity-score-model.md` · `contracts/api-contract.md` (`lead.ia.indisponivel`)
- `docs/architecture/integrations/techlab-ai-integration.md` (capacidade `qualification`, fallback)
