# 01 — Architectural Vision — ASST (Asset Hub)

> Camada de visão (Layer 1 — Architect). Gera contratos, não código.
> Módulo: **ASST** · serviço `asst-service` · pacote `com.journeyos.asst`.

## 1. Intent

ASST é o **repositório único de ativos de conteúdo** do Journey OS. Centraliza a criação, o
versionamento, a aprovação e o reuso de tudo que uma operação de educação digital produz —
páginas de venda, sequências de e-mail, criativos, roteiros, documentos e scripts de SDR — e
adiciona uma camada de inteligência (Asset Studio + Asset Intelligence) que **delega à TechLab
AI** a composição e a classificação de conteúdo. Um asset publicado em ASST é a fonte da
verdade consumida por COMM (mensageria), JRNY (estágios de jornada) e SALE (ofertas).

## 2. Problem Statement

A persona de growth (Marina) coordena a produção de dezenas de ativos por campanha, hoje
espalhados em Drive + Notion + Canva + threads de WhatsApp. As dores concretas:

- **Sem versão vigente confiável** — "qual é o e-mail aprovado?" vira arqueologia de pastas.
- **Sem trilha de aprovação** — Rafael (CEO/Infoprodutor) precisa aprovar copy de oferta, mas a aprovação acontece informalmente e some.
- **Sem reuso** — um roteiro que converteu não é reaproveitável de forma estruturada em outra jornada; é copiado e colado, perdendo proveniência.
- **Produção lenta** — escrever a primeira versão de uma landing/e-mail do zero é gargalo; a IA poderia compor um rascunho a partir de um brief + contexto da empresa.

O Journey OS resolve isso com um hub que trata cada ativo como um **asset versionado** com
**ciclo de aprovação** explícito e **composição assistida por IA**, e que expõe os assets
publicados como insumo de primeira classe para os demais módulos.

## 3. Personas

| Persona | Papel canônico | Relação com ASST |
|---|---|---|
| **Marina — Head de Growth** | `HEAD_GROWTH` | Persona **principal**. Cria assets, usa o Asset Studio para compor rascunhos, organiza por tipo/tag, submete para aprovação. |
| **Rafael — Infoprodutor / CEO** | `INFOPRODUTOR` | Persona **secundária**, mas **autoridade de publicação**: aprova/rejeita assets submetidos e define padrões de conteúdo. |
| **Lucas — SDR / Closer** | `SDR` | Consumidor de leitura: usa scripts/assets publicados; `data_scope` restringe o que enxerga. |
| **Serviços do Journey OS** (COMM, JRNY, SALE) | — (máquina) | Consomem assets **publicados** (Feign/HTTP + eventos) como templates, conteúdo de estágio e copy de oferta. |

## 4. MVP Scope (in)

1. **Asset CRUD + catálogo**: `asset` tipado (`LANDING_PAGE`, `EMAIL`, `CRIATIVO`, `ROTEIRO`, `DOCUMENTO`, `SCRIPT_SDR`) no schema `emp_<slug>`; metadados (título, descrição, tags, dono).
2. **Versionamento**: `versao_asset` **imutável** — revisões numeradas; conteúdo estruturado/texto + referência de binário por URL externa; uma versão vigente publicada por asset.
3. **Approval workflow**: máquina de estados `RASCUNHO → EM_REVISAO → APROVADO → PUBLICADO` (+ `REJEITADO`); registro de `aprovacao` (revisor, decisão, comentário, timestamp).
4. **Asset Studio**: `POST /api/v1/assets/{id}/studio/compose` → compõe/edita conteúdo via TechLab AI `document_composition` a partir de brief + contexto da empresa; resultado vira nova `versao_asset` em `RASCUNHO`.
5. **Asset Intelligence**: classificação/tagging automática via TechLab AI na criação/publicação; indexação no índice Elastic `assets` (dimension).
6. **Busca/listagem**: filtros por `tipo_asset`/tag/estado + full-text via Elastic; paginação.
7. **Consumo cross-módulo**: leitura de assets publicados via Feign (`AssetQueryClient`) + evento `journey-os.asset.versao.publicada`.

## 5. Out of Scope (MVP)

- Edição colaborativa em tempo real (co-editing / CRDT).
- Upload e transcoding de binários pesados (vídeo/imagem) — binários são **referenciados por URL** no MVP, não hospedados pelo ASST.
- Entrega pública / CDN de assets.
- A/B testing de variantes de asset.
- Brand kit / design system avançado (paleta, componentes reutilizáveis).
- Tradução automática multilíngue.
- Aprovação multi-nível com SLA/escalonamento — MVP é aprovação **single-step**.

## 6. Architectural Principles

1. **Hexagonal estrito** — domínio sem Spring/JPA; portas in/out; ArchUnit bloqueante (ver `ADR-001`).
2. **Versão imutável é a verdade** — uma `versao_asset` publicada nunca é editada in-place; corrigir = nova versão (ver `ADR-005`). Proveniência e auditoria preservadas por construção.
3. **IA é capacidade delegada** — toda composição/classificação passa pela TechLab AI via HTTP; o BE **nunca** chama provider de IA direto. TechLab AI fora do ar degrada o Asset Studio, não o CRUD/aprovação (fallback graceful — ver `ADR-003`).
4. **Isolamento por schema** — ASST opera exclusivamente no `emp_<slug>` do tenant corrente; zero vazamento cross-empresa (ver `ADR-004`).
5. **Publicação é um evento de domínio** — publicar um asset emite `asset.versao.publicada`; consumidores reagem sem acoplamento síncrono.
6. **Busca/IA não são fonte da verdade** — Elastic acelera busca e Asset Intelligence; se cair, o PostgreSQL continua sendo a fonte canônica do asset.
7. **Aprovação separa autoria de publicação** — quem cria (HEAD_GROWTH) não é necessariamente quem publica (INFOPRODUTOR); a state machine impede atalhos.

## 7. Success Signals

- Marina compõe um rascunho de e-mail no Asset Studio em < 1 min (brief → versão `RASCUNHO`), em vez de partir da folha em branco.
- Rafael aprova/rejeita um asset submetido e a decisão fica registrada com autor, comentário e timestamp — sempre recuperável.
- COMM busca "o template de boas-vindas publicado" e recebe deterministicamente a versão vigente, com proveniência.
- Publicar um asset propaga `asst.versao.publicada` e atualiza o índice `assets` em < 5 s.
- Nenhuma requisição com JWT da empresa A retorna asset da empresa B (cross-empresa guard).
- TechLab AI indisponível: CRUD, versionamento e aprovação continuam funcionando (apenas o Asset Studio retorna degradação explícita).
- 100% das cláusulas SHALL das specs viram cenário BDD (gate D-218).

---

## Referências

- ADRs: `adr/ADR-001..005`
- Brief: `_brief.md`
- Blueprint: `02-architecture-blueprint.md`
- Multi-tenancy global: `docs/architecture/shared/multi-empresa.md`
- TechLab AI: `docs/architecture/integrations/techlab-ai-integration.md`
- Elastic (`assets`): `docs/architecture/integrations/elastic-data-contract.md`
