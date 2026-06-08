# 03 — Initial Domain Framing — JRNY (Journey & Routing)

> Rascunho de domínio (refinado em `/be-architect-specs` → `contracts/data-model.md`).
> Linguagem ubíqua em pt-BR (identificadores canônicos), alinhada ao padrão WRKS/ASST.

## 1. Ubiquitous Language

| Termo | Definição |
|---|---|
| **Jornada** (`jornada`) | Definição versionada de um funil multi-estágio por `empresa`. Agregado raiz. Possui identidade estável e uma sequência ordenada de estágios. |
| **Estágio** (`estagio`) | Passo ordenado dentro de uma jornada, tipado (`CAPTURA`, `NUTRICAO`, `QUALIFICACAO`, `OFERTA`, `FECHAMENTO`, `POS_VENDA`). Pode referenciar um asset publicado (conteúdo) e ações sinalizadas. |
| **Estado da jornada** (`estado_jornada`) | Posição na máquina de publicação: `RASCUNHO`, `PUBLICADA`, `ARQUIVADA`. |
| **Regra de roteamento** (`regra_roteamento`) | Condição versionada (sobre score/segmento/atributo do lead) que decide o estágio/jornada-alvo. Avaliada pelo Routing Engine. |
| **Routing Engine** (`MotorRoteamento`) | Componente de domínio que avalia regras determinísticas (+ assist de IA opcional) e produz uma decisão de roteamento. |
| **Inscrição na jornada** (`inscricao_jornada`) | Estado de um lead dentro de uma jornada: estágio corrente, data de entrada, histórico de transições. |
| **Decisão de roteamento** (`decisao_roteamento`) | Registro **imutável** de uma decisão do Routing Engine: snapshot de entrada, regra disparada, se houve assist de IA, alvo escolhido, motivo. É o decision log. |
| **Transição de estágio** (`transicao_estagio`) | Movimento de um lead de um estágio para outro (fato append-only). |
| **Assist de IA** | Recomendação de próximo-melhor-estágio da TechLab AI (`orchestration`). Opcional; estado `USADO` / `IGNORADO` / `INDISPONIVEL` registrado na decisão. |
| **Empresa** | Tenant (workspace). Define o schema operacional `emp_<slug>`. |

## 2. Aggregates and Entities (rascunho inicial)

- **Jornada** *(agregado raiz)* — `id`, `empresa_id`, `nome`, `descricao`, `estado_jornada`, `versao` (int), `criado_por`, `criado_em`, `atualizado_em`.
  - **Estagio** *(entidade filha)* — `id`, `jornada_id`, `ordem` (1..N), `tipo_estagio`, `nome`, `asset_ref_id` (nullable — asset publicado de ASST), `terminal` (bool), `config` (jsonb).
  - **RegraRoteamento** *(entidade filha)* — `id`, `jornada_id`, `estagio_origem_id` (nullable = entrada), `estagio_destino_id`, `condicao` (jsonb — score/segmento/atributo), `prioridade` (int), `versao` (int), `ativa` (bool).
- **InscricaoJornada** *(agregado próprio / estado do lead)* — `id`, `empresa_id`, `lead_id`, `jornada_id`, `jornada_versao`, `estagio_corrente_id`, `estado` (`ATIVA`/`CONCLUIDA`/`ENCERRADA`), `entrou_em`, `atualizado_em`.
- **DecisaoRoteamento** *(entidade imutável — decision log)* — `id`, `empresa_id`, `lead_id`, `inscricao_id` (nullable), `gatilho` (evento origem), `snapshot_entrada` (jsonb), `regra_id` (nullable), `assist_ia` (`USADO`/`IGNORADO`/`INDISPONIVEL`), `resultado` (`ROTEADO`/`SEM_MUDANCA`/`NAO_ROTEADO`), `estagio_alvo_id` (nullable), `motivo`, `decidido_em`.
- **Value objects:** `CondicaoRoteamento` (predicado sobre o lead), `SnapshotLead` (score/segmento/atributos no instante da decisão), `RecomendacaoIa` (sugestão da TechLab AI + confiança).

> Agregado consistente: `Jornada` controla seus `Estagio` e `RegraRoteamento` (definição); a
> `InscricaoJornada` é o estado de execução do lead e referencia a **versão** da jornada em que
> entrou. Decisões nunca são mutadas — corrigir = nova decisão.

## 3. Domain Events (inicial)

| Evento | Quando | Payload (resumo) |
|---|---|---|
| `journey-os.jornada.publicada` | Jornada passa a `PUBLICADA` | `jornadaId`, `empresaId`, `versao`, `nome` |
| `journey-os.lead.roteado` | **Evento-âncora** — Routing Engine decide o alvo de um lead | `leadId`, `empresaId`, `jornadaId`, `estagioAlvoId`, `decisaoId`, `assistIa` |
| `journey-os.estagio.transicionado` | Lead muda de estágio | `leadId`, `empresaId`, `jornadaId`, `estagioOrigemId`, `estagioDestinoId` |
| `journey-os.jornada.concluida` | Lead atinge estágio terminal | `leadId`, `empresaId`, `jornadaId`, `inscricaoId` |

Consumidos: `journey-os.lead.qualificado`, `journey-os.lead.score.atualizado`,
`journey-os.lead.segmento.alterado` (LEAD), `journey-os.asset.versao.publicada` (ASST),
`journey-os.modelo.acesso.alterado`, `journey-os.empresa.provisionada` (WRKS).

## 4. State Transitions (alto nível)

### Jornada (definição)

```
   criar               publicar              arquivar
(∅) ────► RASCUNHO ────────────► PUBLICADA ────────────► ARQUIVADA
              ▲                       │ nova versão (editar)
              └──────── nova versão ──┘   (PUBLICADA não é editada in-place)
```

### Inscrição do lead (execução)

```
   rotear (1ª vez)        avançar              atingir terminal
(∅) ───────────────► ATIVA ──────► ATIVA(estágio+1) ──────────────► CONCLUIDA
                       │  encerrar (regra/admin)
                       ▼
                    ENCERRADA
```

- Só `RASCUNHO` é editável; `PUBLICADA` muda apenas via nova `versao` (inscrições ativas seguem na versão de entrada).
- Avanço de estágio só pelo Routing Engine (regra) ou conclusão; nunca salto arbitrário não registrado.
- Toda transição de inscrição gera uma `DecisaoRoteamento` correspondente (auditabilidade).

## 5. Invariants

1. Toda `DecisaoRoteamento` é **imutável** após criada; correção = nova decisão (nunca edição in-place).
2. Um lead tem **no máximo uma** `InscricaoJornada` `ATIVA` por jornada por vez.
3. A `InscricaoJornada` referencia a **versão** da jornada em que entrou; publicar nova versão não altera inscrições ativas.
4. Avanço/roteamento só ocorre por avaliação do Routing Engine; transição inválida → erro de domínio, nunca estado corrompido.
5. O assist de IA (`orchestration`) **nunca** é obrigatório: ausência/falha resulta em decisão determinística com `assist_ia=INDISPONIVEL` — jamais em bloqueio.
6. Toda decisão registra o `snapshot_entrada` que a originou (proveniência/auditoria do "por quê").
7. `empresa_id` de todo registro = `EmpresaContextHolder.require()` (zero cross-empresa).
8. Só jornadas `PUBLICADA` podem matricular/rotear leads; `RASCUNHO`/`ARQUIVADA` não roteiam.

---

## Referências

- `02-architecture-blueprint.md` · `05-persistence-model.md`
- `adr/ADR-005-routing-engine-model.md` (motor determinístico + decision log imutável + assist IA)
- `docs/architecture/integrations/techlab-ai-integration.md` (`orchestration`)
