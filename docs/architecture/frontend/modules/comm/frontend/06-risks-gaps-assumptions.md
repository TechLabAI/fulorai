# 06 — Risks, Gaps & Assumptions — COMM · Frontend

> Riscos de UX/performance/contrato, gaps conhecidos, suposições a validar e dependências críticas.

## 1. Riscos

| # | Risco | Impacto | Mitigação |
|---|---|---|---|
| **R1** | **Polling de entrega** martela o servidor ou vaza timers (sem cleanup) | Carga BE + leaks no FE | ADR-005: backoff + teto + parada no terminal/destroy/empresa-switch; flag `comm.delivery-tracking` para desligar. |
| **R2** | **Latência percebida do rastreio** (polling não é push) decepciona "tempo real" | UX (Success Signal) | Backoff agressivo no início (≈3 s); indicador "atualizando…"; documentar expectativa; migração a SSE é novo ADR se necessário. |
| **R3** | **Degradação da IA** (Template Studio `503`) confundida com falha do módulo | UX / confiança | Princípio 4 (01) + UINV-7: banner explícito "IA indisponível", CTA editar manual; CRUD/roteamento/disparo intactos; flag `comm.template-studio`. |
| **R4** | **Validação de placeholders** divergente entre FE e BE (`variavel-nao-declarada`) | Erros 422 evitáveis | Validação síncrona no editor espelhando a regra BE (UINV-1); testes de paridade FE↔BE no implement. |
| **R5** | **Idempotência mal aplicada** (chave não reusada em retry/duplo-clique) | Mensagens duplicadas | UINV-4: facade gera/reusa `Idempotency-Key` por intenção de disparo; botão desabilita durante o request. |
| **R6** | **Vazamento cross-empresa** ao trocar de empresa com listas/timeline em tela | LGPD / segurança | UINV-9: invalidar todos os signals de COMM e parar polling antes do reload. |
| **R7** | **Bundle size** das 5 features (catálogo, studio, routing, messages, channels) | Performance (TTI) | Lazy por feature (`loadComponent`); patterns shared reutilizados; orçamento de bundle no CI. |
| **R8** | **Confusão canal × provedor** vazando provedor para a UI | Quebra de boundary | O FE só modela `canal`; `provedor` aparece **read-only** no rastreio/config; nunca lógica de provedor no FE. |
| **R9** | **Exposição de segredo de canal** na config | Segurança | UINV-6: a UI só lida com `credencialRef` mascarada; BE nunca retorna o segredo. |

## 2. Gaps Conhecidos

- **OpenAPI / `@journeyos/shared/contracts`**: o BE ainda não expõe OpenAPI consumível; os tipos do FE
  (TemplateVM, MensagemVM, etc.) serão **escritos à mão** a partir do `api-contract.md` até o contrato
  gerado existir (alinhado ao gap global em "Shared libs — contracts").
- **Vínculo a asset (ASST)**: a seleção de um asset publicado como fonte de template precisa de uma
  forma de **buscar/escolher asset** — definir no SPEC se via endpoint do `comm-service` (proxy) ou se
  o FE consulta o `asst-service` por API (preferência: pelo `comm-service`, mantendo boundary).
- **Janela de envio (`janelaEnvio`)**: formato/UX de configuração de janela horária por canal ainda
  não detalhado no contrato — confirmar no SPEC.
- **Disparo a partir de outros módulos**: JRNY/SALE/LEAD acionam via API BE; o ponto de entrada de
  disparo 1:1 na UI COMM (vs. dentro do detalhe do lead em LEAD) precisa ser decidido no SPEC.

## 3. Suposições a Validar

- **A1** — Latência típica de entrega (provedor→webhook→BE) é de segundos a poucos minutos; o backoff
  do polling (≈3 s → ≈15 s) é adequado. _Validar com dados reais; ajustar curva._
- **A2** — Volume de templates por empresa é da ordem de dezenas/baixas centenas (paginação simples
  basta; sem virtualização agressiva no MVP).
- **A3** — Volume de mensagens em lista pode ser alto (milhares) → paginação + filtros server-side
  obrigatórios; sem carregar tudo.
- **A4** — Composição do Template Studio responde em poucos segundos (interação síncrona aceitável,
  como no ASST); se p95 for alto, reavaliar async (novo ADR).
- **A5** — SDR (`SDR`) tem `data_scope` que restringe mensagens/leads visíveis; a UI respeita o escopo
  retornado pelo BE (não filtra client-side por segurança).

## 4. Dependências Críticas

- **WRKS** (fundação): `auth-session`, `empresa-context`, `access-decision` — pré-condição de toda
  rota COMM.
- **`comm-service`** BE: endpoints `/api/v1/{templates,messages,routing-rules,channels}` + estados de
  entrega + `Idempotency-Key`.
- **ASST** (via API BE): assets publicados como fonte de conteúdo de template (sem import `scope:asst`).
- **Shared libs**: `access-http-base`, `ui-tokens/ui-components/ui-feedback`, `error-model`,
  `observability`; patterns `smart-table`/`timeline`/`wizard-form-shell` se disponíveis.
- **Design tokens**: estados visuais de entrega (`ENVIADA`/`ENTREGUE`/`LIDA`/`FALHADA`) e de template
  (`RASCUNHO`/`ATIVO`/`ARQUIVADO`) precisam de cores/ícones canônicos em `@journeyos/shared/ui-tokens`.

---

## Referências

- `01-architectural-vision.md` · `04-frontend-architecture-direction.md` · `05-state-and-data-flow.md`
- ADR-005 (polling) · ADR-003/004 (lazy/registry)
- BE: `docs/architecture/backend/services/comm-service/06-risks-gaps-assumptions.md`
- `docs/architecture/frontend/standards/nx-boundaries.md` · `access-layer-contracts.md`
