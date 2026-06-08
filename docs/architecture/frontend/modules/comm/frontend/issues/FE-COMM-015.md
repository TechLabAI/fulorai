## [FE-COMM-015] feature-channel-config — config de canais por empresa

**Status:** INTACT -- pos-validacao 2026-06-05
**Maturidade:** 18 -- Inicial
**Done/Total:** 0/4 itens
**GitHub:** [#TBD]

**Outcome:**
`ChannelConfigPageComponent` + `ChannelListComponent`/`ChannelRowComponent` + `ChannelConfigDialogComponent`
(canal/provedor/identidade/credencialRef/janelaEnvio). `credencialRef` mascarada; segredo nunca exibido/coletado em claro.

**Context / Problem statement:**
- Pré-condição de disparo real. Fonte: SPEC-02, SPEC-03 (UINV-6). Depende: FE-COMM-008.

**Approach:**
1) Lista de canais com `credencialRefMascarada` + estado ativo.
2) Dialog cria/edita (gated por `comm.canal.configurar`); duplicado (canal, provedor) → erro inline (C-07.5).
3) Tratar `credencialRef` como referência (nunca segredo).

**Non-goals:** gestão de secret manager (BE); least-cost routing (fora de escopo).

**Layer(s):** frontend / `libs/comm/feature-channel-config`
**Bounded context:** comm
**Service execution spec(s):** `SPEC-02`, `SPEC-03`, `SPEC-07`
**Architecture alignment:** standalone/OnPush; UINV-6; tag `scope:comm` `type:feature`.

**Implementation checklist (by file):**
- 🔲 [MISSING] `libs/comm/feature-channel-config/src/lib/channel-config.page.ts`
- 🔲 [MISSING] `libs/comm/feature-channel-config/src/lib/channel-config.dialog.ts` (UINV-6: `credencialRef` mascarada / segredo nunca em claro — invariante de seguranca ainda nao implementada)

**Tests**
- 🔲 [MISSING] `nx test comm-feature-channel-config` PASS · 🔲 [MISSING] `nx lint` PASS

**Milestone:** Wave P3 / Feature libs
**Labels:** type:feature · layer:frontend · scope:comm · priority:P3

**Acceptance criteria:**
- Segredo nunca exibido; duplicado bloqueado inline; `nx test/lint/build` PASS

**Dependencies:** FE-COMM-008
**API / Contract impact:** `/api/v1/channels`.
**Risks / Notes:** cobre C-02.6, C-04.6, C-07.5.
