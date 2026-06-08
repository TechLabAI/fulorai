# ADR-005 — Asset Studio: composição assistida síncrona com degradação graciosa

- **Status:** accepted

## Contexto

O **Asset Studio** é o diferencial do ASST: compor/editar conteúdo de asset a partir de um brief +
contexto da empresa, usando IA. No Journey OS, **toda capacidade de IA é delegada à TechLab AI** e
**nunca chamada direto** — nem pelo BE (que chama a TechLab AI via HTTP), nem pelo FE (que chama
**apenas** o `asst-service`). O contrato BE (`POST /api/v1/assets/{id}/studio/compose`) é
**síncrono**: retorna `201` com a nova versão (`origem=ASSET_STUDIO`, estado `RASCUNHO`) ou
`503 asst.studio.ia-indisponivel` quando a TechLab AI está fora/timeout — e, nesse caso, **nenhuma
versão é criada**. A composição pode levar alguns segundos. O FE precisa decidir como modelar essa
interação sem degradar o resto do módulo nem violar a regra de não-chamar-IA-direto.

## Decisão

1. **O FE chama somente o BE.** `StudioApiService.compose()` (`libs/asst/data-access`) bate em
   `POST /studio/compose`; o FE **nunca** conhece nem chama a TechLab AI. O `feature-asset-studio`
   consome a facade, não o HttpClient direto (UINV-2).
2. **Interação síncrona com loading explícito.** A facade expõe um signal `studioState`:
   `idle → composing → draft-pronto | degradado`. Durante `composing`, a UI mostra progresso e
   bloqueia apenas o formulário do Studio (sem otimismo — a versão só aparece após o `201`).
3. **Degradação graciosa.** `503 asst.studio.ia-indisponivel` (ou timeout) → `studioState='degradado'`,
   banner explicativo e CTA "compor manualmente" (criar versão via `POST /{id}/versoes`,
   `origem=MANUAL`). A falha da IA **nunca** bloqueia catálogo, versionamento manual ou aprovação
   (UINV-7). A feature flag `asst.asset-studio` permite desligar o Studio inteiro sem afetar o resto.
4. **Proveniência preservada.** A versão produzida carrega `origem=ASSET_STUDIO` e o `briefComposicao`;
   a UI exibe um badge de origem no histórico de versões, e o usuário **revisa** o rascunho antes de
   submeter (o Studio nunca publica automaticamente).
5. **Idempotência.** Onde o BE aceitar `Idempotency-Key`, a facade o utiliza para evitar dupla
   composição em replay.

## Alternativas consideradas

1. **Async com polling / websocket** (job de composição em background) — rejeitada no MVP: o contrato
   BE é síncrono e a latência esperada é de poucos segundos (A-2). Reavaliar via novo ADR se o p95
   provar alto.
2. **FE chamar a TechLab AI direto** — **proibido** pela regra do projeto (nunca chamar provider/IA
   direto); romperia o boundary e a observabilidade centralizada.
3. **Falha da IA bloquear o módulo** (erro global) — rejeitada: violaria o princípio de degradação
   graciosa; o valor do ASST (catálogo/versão/aprovação) não depende da IA.
4. **Publicar automaticamente o resultado da composição** — rejeitada: viola "aprovação separa autoria
   de publicação"; o rascunho precisa de revisão humana.

## Consequências

- **Positivas:** o ASST entrega valor mesmo com a IA fora; boundary respeitado (FE→BE→TechLab AI);
  proveniência e revisão humana garantidas; UX previsível com `studioState`.
- **Negativas:** uma composição longa segura o request síncrono (mitigado por timeout/feedback);
  se a IA ficar consistentemente lenta, será preciso migrar para async (novo ADR) — a facade isola
  esse risco atrás de `studioState`.

## Referências

- BE: `docs/architecture/backend/services/asst-service/contracts/api-contract.md` §3 (Asset Studio)
- BE: `docs/architecture/backend/services/asst-service/contracts/techlab-ai-integration.md`
- `docs/architecture/integrations/techlab-ai-integration.md` (contrato BE ↔ TechLab AI)
- `01-architectural-vision.md` §6 (princípio 4) · `03-domain-framing-frontend.md` (UINV-7)
- `05-state-and-data-flow.md` §5 (mapeamento de `503`)
