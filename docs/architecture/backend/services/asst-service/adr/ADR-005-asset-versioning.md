# ADR-005 — Versionamento imutável + máquina de estados de aprovação/publicação

**Status:** accepted

## Contexto

A dor central do Asset Hub é a perda de proveniência: ninguém sabe qual é a versão vigente de
um asset, quem aprovou, ou o que mudou entre revisões. Além disso, conteúdo gerado por IA
(Asset Studio) **não pode** ir direto à publicação sem revisão humana. Precisamos de um modelo
que torne histórico e aprovação invioláveis por construção.

## Decisão

1. **Versão imutável (copy-on-write):** cada `versao_asset` é imutável após criada. Correção ou
   nova composição = **nova versão** com `numero` incremental. Editar in-place é proibido no
   domínio (invariante). O conteúdo (`conteudo` jsonb), os binários referenciados e o
   `brief_composicao` (se origem `ASSET_STUDIO`) ficam congelados na versão.

2. **Máquina de estados de aprovação** controlada pelo agregado raiz `Asset`:
   ```
   RASCUNHO → EM_REVISAO → APROVADO → PUBLICADO
       ▲          │ (rejeitar)
       └ nova ver ▼
              REJEITADO
   qualquer → ARQUIVADO (soft delete)
   ```
   - Só `EM_REVISAO` aceita aprovar/rejeitar; só `APROVADO` aceita publicar.
   - Publicar promove a versão a **vigente** (`versao_vigente_id`); a anterior permanece como
     histórico `PUBLICADO` (não é apagada).
   - Asset Studio sempre cria versão em `RASCUNHO` — **nunca** publica direto (garante revisão humana).

3. **Segregação autor/aprovador:** registrada sempre (`aprovacao.revisor_id`); obrigatória se a
   política da empresa exigir (MVP: configurável, default permite autor = aprovador mas registra).

## Alternativas consideradas

- **Edição mutável + campo `versao` numérico:** simples, mas perde o conteúdo histórico e a proveniência (não dá para auditar o que a IA gerou e foi aprovado). Rejeitada.
- **Publicação direta sem state machine:** rápida, mas remove o controle de qualidade/aprovação — risco alto de publicar conteúdo IA incorreto (R4 em `06`). Rejeitada.
- **Versionamento por event sourcing puro:** poderoso, mas excessivo para o MVP; o modelo de versões imutáveis + state machine entrega a proveniência necessária com complexidade menor. Adiado.

## Consequências

**Positivas:** histórico e aprovação invioláveis; rollback trivial (apontar `versao_vigente_id` para versão anterior); proveniência de conteúdo IA garantida; auditoria/LGPD por construção.

**Negativas:** acúmulo de versões (mitigado: conteúdo leve, binários por URL, arquivamento); a state machine precisa de testes BDD cobrindo todas as transições (gate D-218).

## Referências

- `03-initial-domain-framing.md` (§4 State Transitions, §5 Invariants)
- `05-persistence-model.md` (`versao_asset`, `aprovacao`)
- `adr/ADR-003-messaging-strategy.md` (publicação emite `asset.versao.publicada`)
