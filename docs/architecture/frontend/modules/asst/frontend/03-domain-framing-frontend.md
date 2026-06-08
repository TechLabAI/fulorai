# 03 — Domain Framing (Frontend) — ASST

> Espelho do domínio BE (`asst-service/03-initial-domain-framing.md`) **sem redefinir** termos.
> Aqui mapeamos View Models, UI Events, transições de estado de UI e invariantes client-side.

## 1. Ubiquitous Language (referência ao BE — não redefinir)

Os termos canônicos vivem no BE (`_brief.md` + `03-initial-domain-framing.md` do `asst-service`).
Resumo dos que a UI manipula diretamente:

| Termo | Uso na UI |
|---|---|
| **Asset** | Item do catálogo; entidade central tipada por `tipoAsset`. Tem estado e versão vigente. |
| **tipoAsset** | Enum (`LANDING_PAGE`, `EMAIL`, `CRIATIVO`, `ROTEIRO`, `DOCUMENTO`, `SCRIPT_SDR`) — chip/filtro e ícone na UI. |
| **Versão (versao_asset)** | Item imutável do histórico; conteúdo estruturado/texto + binários por URL; tem `numero`, `estado`, `origem`. |
| **Versão vigente** | A versão **publicada** corrente (`versaoVigenteId`); destacada no detalhe. |
| **Estado do asset** | `RASCUNHO` / `EM_REVISAO` / `APROVADO` / `PUBLICADO` / `REJEITADO` / `ARQUIVADO` — chip de estado; dirige quais ações aparecem. |
| **Origem da versão** | `MANUAL` ou `ASSET_STUDIO` — badge de proveniência. |
| **Aprovação** | Registro (revisor, decisão, comentário, timestamp) exibido no histórico de aprovação. |
| **Asset Studio** | Capacidade de composição assistida (IA) — formulário de brief → nova versão. |
| **Brief de composição** | Texto/instrução que o usuário fornece ao Studio; gravado na versão para proveniência. |
| **Tag** | Rótulo livre para organização/busca; filtro no catálogo. |
| **Permissão** | `asst.<recurso>.<acao>` — usada por `AccessDecisionService.can()`; dirige visibilidade de ações. |
| **AccessDecision** | Resultado consumido pela Access Layer; o FE **não** o calcula, apenas consome. |
| **Data Scope** | Restringe quais assets o usuário enxerga; o FE só transmite — enforcement é BE. |

## 2. View Models (rascunho por tela)

> VMs são contratos de UI; serão refinados em `/fe-architect-specs` (SPEC-03 / vm-contracts).

```ts
type TipoAsset   = 'LANDING_PAGE' | 'EMAIL' | 'CRIATIVO' | 'ROTEIRO' | 'DOCUMENTO' | 'SCRIPT_SDR';
type EstadoAsset = 'RASCUNHO' | 'EM_REVISAO' | 'APROVADO' | 'PUBLICADO' | 'REJEITADO' | 'ARQUIVADO';
type OrigemVersao = 'MANUAL' | 'ASSET_STUDIO';

// Catálogo (linha/resumo)
AssetResumoVM   { id: string; tipoAsset: TipoAsset; titulo: string; estado: EstadoAsset;
                  tags: string[]; versaoVigenteNumero: number | null; atualizadoEm: string }

// Filtro do catálogo
AssetFiltroVM   { tipo?: TipoAsset; estado?: EstadoAsset; tag?: string; q?: string;
                  page: number; size: number }

// Detalhe do asset
AssetDetailVM   { id: string; tipoAsset: TipoAsset; titulo: string; descricao: string;
                  estado: EstadoAsset; tags: string[]; donoId: string;
                  versaoVigenteId: string | null; versoes: VersaoResumoVM[] }

// Versão (histórico + conteúdo)
VersaoResumoVM  { id: string; numero: number; estado: 'RASCUNHO' | 'PUBLICADA';
                  origem: OrigemVersao; criadoEm: string; vigente: boolean }
VersaoDetailVM  { id: string; numero: number; conteudo: unknown; binarios: BinarioRefVM[];
                  origem: OrigemVersao; briefComposicao?: string }
BinarioRefVM    { url: string; mime: string }

// Formulários
NovoAssetForm   { tipoAsset: TipoAsset; titulo: string; descricao: string; tags: string[] }
NovaVersaoForm  { conteudo: unknown; binarios: BinarioRefVM[] }
StudioComposeForm { brief: string; contexto: Record<string, unknown>; baseVersaoNumero?: number }

// Aprovação
ApprovalItemVM  { assetId: string; titulo: string; tipoAsset: TipoAsset; versaoNumero: number;
                  submetidoEm: string; submetidoPor: string }
ApprovalDecisionForm { decisao: 'APROVADO' | 'REJEITADO'; comentario: string }
AprovacaoVM     { revisor: string; decisao: 'APROVADO' | 'REJEITADO'; comentario: string; decididoEm: string }
```

## 3. UI Events (disparados pelo usuário → mudam state)

| Evento de UI | Origem | Efeito |
|---|---|---|
| `asset.filter.changed` | filtros/busca do catálogo | recarrega lista (`GET /` com query) |
| `asset.created` | form "novo asset" | `POST /` → asset em `RASCUNHO` |
| `asset.metadata.saved` | form de metadados | `PATCH /{id}` (título/descrição/tags) |
| `asset.archived` | ação arquivar | `POST /{id}/arquivar` |
| `version.created` | form "nova versão" | `POST /{id}/versoes` (origem MANUAL) |
| `studio.compose.submitted` | form do Asset Studio | `POST /{id}/studio/compose` (origem ASSET_STUDIO) |
| `asset.submitted` | ação submeter | `POST /{id}/submit` → `EM_REVISAO` |
| `asset.approval.decided` | form aprovar/rejeitar | `POST /{id}/approve` → `APROVADO`/`REJEITADO` |
| `asset.published` | ação publicar | `POST /{id}/publish` → `PUBLICADO` (versão vigente) |

## 4. State Transitions (nível de UI)

**Estado do asset (espelho da state machine BE; a UI deriva as ações disponíveis do estado):**
```
[RASCUNHO] --submit--> [EM_REVISAO] --aprovar--> [APROVADO] --publish--> [PUBLICADO]
[EM_REVISAO] --rejeitar--> [REJEITADO] --(nova versão)--> [RASCUNHO]
[PUBLICADO] --(nova versão)--> [RASCUNHO]   (publicar nova versão atualiza versaoVigenteId)
[qualquer estado não-publicado] --arquivar--> [ARQUIVADO]
```

**Asset Studio (composição):**
```
[idle] --compose--> [composing] --201--> [draft-pronto(RASCUNHO)] | --503--> [degradado(IA indisponível)]
```

**Carregamento de qualquer tela de dados (padrão):**
```
[idle] --load--> [loading] --ok--> [success] | --erro--> [error(AppError)]
```

## 5. Invariants (client-side)

- **UINV-1** Nenhuma rota protegida renderiza sem sessão autenticada **e** empresa ativa — garantido
  por `authGuard` + `empresaGuard`.
- **UINV-2** A UI **nunca** decide RBAC localmente: visibilidade de menu/ação só via
  `AccessDecisionService.can('asst.<perm>')` / `NavigationService`.
- **UINV-3** `empresaId` lido **somente** de `EmpresaContextService` — nunca do JWT decodificado.
- **UINV-4** A UI **nunca** edita uma `versao_asset` existente in-place; a única forma de alterar
  conteúdo é **criar nova versão** (reflexo client-side da imutabilidade `asst.versao.imutavel`).
- **UINV-5** As ações de workflow (submit/approve/publish) são **derivadas do estado atual** do asset;
  a UI não oferece transições inválidas (ex.: publicar fora de `APROVADO`). O BE é a autoridade final
  (`409 asst.estado.transicao-invalida`).
- **UINV-6** Campos obrigatórios validados síncronamente: `titulo` (não vazio), `tipoAsset` (enum),
  `comentario` na **rejeição** (obrigatório), `brief` no Studio (não vazio), `url` de binário (formato).
- **UINV-7** Falha da IA no Asset Studio (`503 asst.studio.ia-indisponivel`) **nunca** bloqueia
  catálogo, versão manual ou aprovação — degrada **apenas** o Studio, com mensagem explícita.
- **UINV-8** Troca de empresa **invalida** catálogo/detalhe da empresa anterior antes de mostrar os
  novos (sem "piscar" asset cross-empresa).

---

## Referências

- BE: `docs/architecture/backend/services/asst-service/03-initial-domain-framing.md`
- BE: `docs/architecture/backend/services/asst-service/contracts/api-contract.md`
- `05-state-and-data-flow.md` · ADR-005 (Asset Studio / degradação da IA)
