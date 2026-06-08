# 03 — Initial Domain Framing — ASST (Asset Hub)

> Rascunho de domínio (refinado em `/be-architect-specs` → `contracts/data-model.md`).
> Linguagem ubíqua em pt-BR (identificadores canônicos), alinhada ao padrão WRKS.

## 1. Ubiquitous Language

| Termo | Definição |
|---|---|
| **Asset** | Ativo de conteúdo gerenciado pelo hub (landing, e-mail, criativo, roteiro, documento, script). Agregado raiz. Possui identidade estável e N versões. |
| **Tipo de asset** (`tipo_asset`) | Classificação do asset: `LANDING_PAGE`, `EMAIL`, `CRIATIVO`, `ROTEIRO`, `DOCUMENTO`, `SCRIPT_SDR`. |
| **Versão de asset** (`versao_asset`) | Revisão **imutável** e numerada do conteúdo do asset. Carrega o conteúdo estruturado/texto + referências de binário (URL). |
| **Estado do asset** (`estado_asset`) | Posição na máquina de aprovação: `RASCUNHO`, `EM_REVISAO`, `APROVADO`, `PUBLICADO`, `REJEITADO`, `ARQUIVADO`. |
| **Aprovação** (`aprovacao`) | Registro de uma decisão de revisão (revisor, decisão aprovar/rejeitar, comentário, data). |
| **Versão vigente** | A `versao_asset` atualmente `PUBLICADO` e exposta para consumo cross-módulo. |
| **Asset Studio** | Capacidade de composição/edição assistida por IA (TechLab AI `document_composition`). Produz uma nova `versao_asset` em `RASCUNHO`. |
| **Asset Intelligence** | Classificação/tagging automática + indexação no índice Elastic `assets`. |
| **Tag** (`tag_asset`) | Rótulo livre ou sugerido por IA, usado para organização e busca. |
| **Empresa** | Tenant (workspace). Define o schema operacional `emp_<slug>`. |

## 2. Aggregates and Entities (rascunho inicial)

- **Asset** *(agregado raiz)* — `id`, `empresa_id`, `tipo_asset`, `titulo`, `descricao`, `estado_asset`, `versao_vigente_id` (nullable), `dono_id` (usuário), `tags[]`, `criado_em`, `atualizado_em`.
  - **VersaoAsset** *(entidade filha, imutável)* — `id`, `asset_id`, `numero` (1..N), `conteudo` (jsonb/text estruturado), `binarios[]` (URLs + metadados), `origem` (`MANUAL` | `ASSET_STUDIO`), `estado` (`RASCUNHO` | `PUBLICADA`), `criado_por`, `criado_em`.
  - **Aprovacao** *(entidade filha)* — `id`, `asset_id`, `versao_id`, `revisor_id`, `decisao` (`APROVADO` | `REJEITADO`), `comentario`, `decidido_em`.
- **Value objects:** `ConteudoComposto` (resultado do Asset Studio), `ReferenciaBinario` (url, mime, tamanho), `BriefComposicao` (prompt/contexto enviado à TechLab AI).

> Agregado consistente: `Asset` controla suas `VersaoAsset` e `Aprovacao`; transições de
> estado só ocorrem pelo agregado raiz (invariantes no domínio).

## 3. Domain Events (inicial)

| Evento | Quando | Payload (resumo) |
|---|---|---|
| `journey-os.asset.criado` | Asset criado (RASCUNHO) | `assetId`, `empresaId`, `tipoAsset`, `donoId` |
| `journey-os.asset.aprovado` | Versão aprovada por revisor | `assetId`, `versaoId`, `revisorId` |
| `journey-os.asset.rejeitado` | Versão rejeitada | `assetId`, `versaoId`, `revisorId`, `motivo` |
| `journey-os.asset.versao.publicada` | **Evento-âncora** — versão vira vigente | `assetId`, `versaoId`, `numero`, `tipoAsset`, `empresaId` |

Consumidos: `journey-os.modelo.acesso.alterado` (WRKS), `journey-os.empresa.provisionada` (WRKS).

## 4. State Transitions (alto nível)

```
            criar                     submeter                aprovar            publicar
   (∅) ─────────────► RASCUNHO ──────────────► EM_REVISAO ──────────► APROVADO ──────────► PUBLICADO
                         ▲                          │  rejeitar                                  │
                         │                          ▼                                            │
                         └───────── nova versão ── REJEITADO                                     │
                                                                                                 ▼
   PUBLICADO ── nova versão (compose/editar) ──► RASCUNHO (v+1)        qualquer ──► ARQUIVADO (soft)
```

- Só `EM_REVISAO` pode ser aprovado/rejeitado. Só `APROVADO` pode ser publicado.
- Publicar uma nova versão **não** apaga a anterior — preserva histórico (versão vigente muda).
- `ARQUIVADO` é exclusão lógica (mantém trilha para auditoria/LGPD).

## 5. Invariants

1. Toda `VersaoAsset` é **imutável** após criada; correção = nova versão (número incremental).
2. Um asset tem **no máximo uma** versão vigente (`PUBLICADO`) por vez.
3. Transição de estado só pelo agregado raiz e apenas se permitida pela máquina de estados (transição inválida → erro de domínio, nunca estado corrompido).
4. **Autor ≠ aprovador** quando a política da empresa exigir segregação (MVP: configurável; default permite, mas registra quem aprovou).
5. Asset Studio sempre gera versão em `RASCUNHO` (nunca publica direto).
6. `empresa_id` de todo registro = `EmpresaContextHolder.require()` (zero cross-empresa).
7. Conteúdo composto pela IA é sempre rastreável à sua `origem=ASSET_STUDIO` + `briefComposicao` (proveniência/auditoria).

---

## Referências

- `02-architecture-blueprint.md` · `05-persistence-model.md`
- `adr/ADR-005-asset-versioning.md` (versionamento imutável + state machine)
- `docs/architecture/integrations/techlab-ai-integration.md` (`document_composition`)
