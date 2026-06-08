# ADR-005 — Contexto multi-empresa e troca em runtime

- **Status:** accepted

## Contexto

Um usuário do Journey OS pode pertencer a várias `empresa`s (workspaces) e precisa **trocar de
empresa sem recarregar** o app. A multi-tenancy é `schema-per-tenant` no BE; no FE, todo dado é
escopado por `empresaId` e **não pode vazar** entre empresas (risco LGPD crítico — R-2). WRKS é o
módulo que materializa a seleção e a troca, mas o `empresaId` ativo é um concern **cross-cutting**.

## Decisão

1. `EmpresaContextService` (`@journeyos/shared/empresa-context`) é a **única fonte de verdade** do
   `empresaId` ativo no FE. Nunca ler `empresaId` do JWT decodificado nem de storage (UINV-3).
2. WRKS **alimenta** a lista de empresas (via `feature-empresa-select` / `data-access`) e **consome**
   o sinal de empresa ativa; o interceptor de `access-http-base` injeta `X-Empresa-Id` automaticamente.
3. **Troca de empresa** (`EmpresaContextService.switchTo(empresaId)`):
   - emite novo JWT (via BE) com o novo `empresa_id`;
   - **cancela requisições in-flight** escopadas à empresa anterior;
   - **invalida caches escopados** explicitamente;
   - **re-avalia** AccessDecision + navegação (`NavigationService`);
   - atualiza a UI **sem refresh completo**.
4. Rotas pré-contexto (`/login`, `/auth/callback`, `/empresa-select`) usam `authGuard` apenas;
   rotas pós-contexto adicionam `empresaGuard`.

## Alternativas consideradas

1. **`empresaId` lido do JWT em cada feature** — rejeitada: duplica fonte de verdade e abre brecha
   de vazamento cross-empresa.
2. **Reload completo na troca de empresa** — rejeitada: UX ruim e perde estado de navegação.
3. **Cada módulo gerencia seu próprio empresa-context** — rejeitada: viola o caráter cross-cutting
   e a Access Layer.

## Consequências

- **Positivas:** isolamento cross-empresa garantido por design; troca instantânea; um só ponto de
  verdade; testável (e2e de não-vazamento).
- **Negativas:** exige que toda `data-access` respeite cancelamento/invalidação na troca; disciplina
  para nunca tocar `empresaId` fora do `EmpresaContextService`.

## Referências

- `docs/architecture/frontend/standards/access-layer-contracts.md` §Multi-empresa
- `docs/architecture/shared/blueprint-core.md` (RULE-07 / `X-Empresa-Id`)
- BE espelho: `wrks-service` ADR-002 (identity authority) · `03-initial-domain-framing.md` (INV-6)
- `05-state-and-data-flow.md` §3 (cache escopado)
