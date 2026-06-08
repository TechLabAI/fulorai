# 03 — Domain Framing (Frontend) — COMM

> Espelho da linguagem ubíqua do BE (`comm-service`), recortada para a UI. Não redefine o domínio;
> projeta View Models, eventos de UI, transições de estado e invariantes client-side.

## 1. Ubiquitous Language (espelho do BE)

| Termo | Significado (não redefinir — ver BE `03`/`_brief.md`) |
|---|---|
| **Template** (`template_mensagem`) | Mensagem reutilizável tipada por `canal` + `tipo`, com corpo contendo placeholders `{{variavel}}`; estado `RASCUNHO/ATIVO/ARQUIVADO`; `versao` incremental. |
| **Canal** | `WHATSAPP` · `EMAIL` · `TELEGRAM` · `SMS`. O FE conhece **só** o canal, nunca o provedor. |
| **Tipo de template** | `TRANSACIONAL` · `MARKETING` · `NOTIFICACAO`. |
| **Template Studio** | Composição assistida por IA (BE delega à TechLab AI); produz novo corpo `RASCUNHO`. |
| **Regra de roteamento** (`regra_roteamento`) | Condições + `canalPreferido` + `canaisFallback` + `templateId` + `prioridade` + `ativa`. |
| **Mensagem** (`mensagem`) | Disparo renderizado de um template ATIVO + variáveis, escopado a um lead; tem `estadoEntrega`. |
| **Estado de entrega** | `PENDENTE → ENFILEIRADA → ENVIADA → ENTREGUE → LIDA` (+ `FALHADA`). |
| **Evento de entrega** (`evento_entrega`) | Item append-only do ciclo de vida (`tipo`, `ocorridoEm`), alimentado por callbacks do provedor. |
| **Config de canal** (`config_canal`) | Provedor + identidade de remetente + `credencialRef` (referência, nunca o segredo) por empresa. |
| **Idempotency-Key** | Chave que garante um único envio por disparo (replay-safe). |

## 2. View Models (rascunho por tela)

```ts
// Catálogo de templates
TemplateResumoVM { id; nome; canal: Canal; tipo: TipoTemplate; estado: EstadoTemplate; versao: number; atualizadoEm: string }

// Editor / detalhe de template
TemplateVM {
  id; nome; canal; tipo; estado; versao;
  assunto?: string;            // obrigatório quando canal=EMAIL
  corpo: string;               // contém placeholders {{variavel}}
  variaveis: string[];         // declaradas
  assetOrigemId?: string|null; // vínculo opcional a asset publicado
  acoesDisponiveis: TemplateAcao[]; // computed por estado + permissão
}

// Template Studio
StudioFormVM { brief: string; contexto: Record<string,unknown>; assetOrigemId?: string }
StudioStateVM = 'idle' | 'composing' | 'draft-pronto' | 'degradado'

// Regra de roteamento
RegraRoteamentoVM { id; nome; prioridade: number; condicoes: Record<string,unknown>;
  canalPreferido: Canal; canaisFallback: Canal[]; templateId: string; ativa: boolean }

// Mensagem (lista + detalhe)
MensagemResumoVM { id; leadId; canal: Canal; estadoEntrega: EstadoEntrega; criadoEm: string }
MensagemVM { id; leadId; canal; estadoEntrega; provedor?: string; provedorMessageId?: string;
  tentativas: number; motivoFalha?: string; criadoEm; atualizadoEm;
  eventos: EventoEntregaVM[];  // timeline
  estadoTerminal: boolean;     // computed -> para o polling
}
EventoEntregaVM { tipo: EstadoEntrega; ocorridoEm: string }

// Config de canal
ConfigCanalVM { id; canal: Canal; provedor: string; identidadeRemetente: string;
  credencialRefMascarada: string; ativo: boolean }
```

## 3. UI Events (disparam mudança de estado)

- `templateCreated`, `templateEdited`, `templateActivated`, `templateArchived`
- `studioComposeRequested`, `studioDraftAccepted`, `studioFailed` (degradado)
- `routingRuleCreated`, `routingRuleEdited`
- `messageDispatchRequested`, `messageDispatchAccepted`, `messageDispatchRejected`
- `deliveryPollTick`, `deliveryStateAdvanced`, `deliveryReachedTerminal`
- `channelConfigured`, `channelEdited`
- `empresaChanged` (vinda da Access Layer) → invalida catálogo/mensagens/regras/canais em tela

## 4. State Transitions (nível de UI)

```
# Carregamento genérico de lista/detalhe
idle -> loading -> success | empty | error

# Template (espelho do estado de domínio)
RASCUNHO --(Ativar / accessGuard comm.template.publicar)--> ATIVO --(Arquivar)--> ARQUIVADO
RASCUNHO --(Arquivar)--> ARQUIVADO
# ATIVO é pré-condição de disparo (UI bloqueia disparo de não-ATIVO)

# Template Studio
idle -> composing -> draft-pronto      # 200: novo corpo RASCUNHO para revisão
            \-> degradado              # 503: corpo inalterado, CTA editar manual

# Mensagem (rastreio — polling enquanto não-terminal)
PENDENTE -> ENFILEIRADA -> ENVIADA -> ENTREGUE -> LIDA   (terminais: LIDA, FALHADA)
                     \-------------------> FALHADA
```

## 5. Invariants (client-side)

- **UINV-1** — Toda placeholder `{{x}}` usada em `corpo` deve estar em `variaveis` (validação síncrona antes do PATCH; espelha `comm.template.variavel-nao-declarada`).
- **UINV-2** — `canal=EMAIL` exige `assunto` não-vazio (validação síncrona; espelha `comm.template.assunto-obrigatorio`).
- **UINV-3** — Disparo só é habilitado para template em estado `ATIVO`; a UI não oferece "enviar" de RASCUNHO/ARQUIVADO.
- **UINV-4** — Todo disparo envia `Idempotency-Key`; duplo-clique reusa a mesma chave (sem segundo POST).
- **UINV-5** — A UI **nunca** chama provider de IA nem a TechLab AI; o Template Studio fala só com a facade (`/studio/compose`).
- **UINV-6** — A UI **nunca** exibe nem coleta o segredo de provedor — apenas `credencialRef` (mascarada).
- **UINV-7** — Falha da IA (`503`) **não** bloqueia catálogo/editor/roteamento/disparo/rastreio; só o Studio degrada.
- **UINV-8** — O polling de entrega para ao atingir estado terminal (`LIDA`/`FALHADA`) ou ao sair da tela (cleanup), com backoff e teto de tentativas.
- **UINV-9** — Toda leitura/escrita é escopada pela empresa ativa; trocar de empresa limpa o estado em tela antes de recarregar (sem vazamento cross-empresa).
- **UINV-10** — Campos de criação obrigatórios (`nome`, `canal`, `tipo`) validados antes do POST (espelha `comm.template.*-obrigatorio`).

---

## Referências

- BE domínio: `docs/architecture/backend/services/comm-service/03-initial-domain-framing.md`
- BE API + erros: `docs/architecture/backend/services/comm-service/contracts/api-contract.md` §1–6
- `05-state-and-data-flow.md` (mapa de signals + erros) · ADR-002 (signals) · ADR-005 (polling)
