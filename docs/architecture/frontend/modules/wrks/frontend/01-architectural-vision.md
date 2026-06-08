# 01 — Architectural Vision — WRKS (Workspace & Identity) · Frontend

> Camada de visão FE (Layer 1 — Architect). Gera contratos de UI, não código Angular.
> Módulo **WRKS** · module `wrks` · app lazy `apps/wrks` · libs `libs/wrks/*` · scope `scope:wrks`.
> Espelha o domínio do `wrks-service` (BE); aqui o recorte é a **experiência do usuário**.

## 1. Intent (UX-driven)

Ao final, o usuário do Journey OS consegue, a partir de uma superfície única:

1. **Entrar** com um login único (Keycloak OIDC) sem o app reimplementar autenticação.
2. **Escolher a empresa** (workspace) em que vai operar quando pertence a várias — e trocar
   de empresa a qualquer momento **sem recarregar** o app.
3. **Administrar o workspace** (persona Rafael): ver e editar dados da empresa, configurar a
   org structure (business units / teams), convidar usuários, atribuir papéis canônicos e
   `data_scope`, ativar/desativar acessos.
4. **Enxergar exatamente o que seu papel permite** — toda a UI (menus, ações, rotas) é derivada
   da Access Layer; um `SDR` simplesmente não vê as telas de administração.

WRKS é a **fundação de identidade do FE**: é o primeiro módulo a carregar e a precondição de
qualquer outra tela da plataforma. Ele não tem "domínio de negócio" próprio rico — seu produto
é **acesso correto e contexto de empresa confiável** para todos os demais.

## 2. Problem Statement (jornada atual vs nova)

**Jornada atual (Rafael):** acessos espalhados por Hotmart, ActiveCampaign, Meta Ads e planilhas;
cada ferramenta com seu login; impossível dizer de forma confiável "Marina vê a operação inteira,
Lucas vê só a fila de leads dele". Onboarding de um novo membro é manual e propenso a erro; não
há uma noção de *workspace* isolado por operação.

**Jornada nova (Journey OS · WRKS FE):** um login; uma tela de seleção de empresa para quem opera
múltiplas operações; uma área de administração onde papéis canônicos (`INFOPRODUTOR`,
`HEAD_GROWTH`, `SDR`) são atribuídos em segundos e refletem em toda a plataforma. A UI de cada
usuário é **montada a partir das permissões** — não há tela "escondida por convenção", há tela
**ausente por decisão de acesso**.

## 3. Personas (job-to-be-done)

| Persona | Papel canônico | Job-to-be-done no WRKS FE |
|---|---|---|
| **Rafael — Infoprodutor / CEO** | `INFOPRODUTOR` | "Quero montar minha operação no Journey OS: criar/configurar a empresa, trazer minha equipe e definir quem faz o quê — em minutos, sem TI." |
| **Marina — Head de Growth** | `HEAD_GROWTH` | "Quero gerenciar minha business unit e meu time, e operar a empresa inteira que me cabe, sem mexer em config global." |
| **Lucas — SDR / Closer** | `SDR` | "Quero entrar, escolher a empresa certa e ir direto para a minha fila — sem ver telas de admin que não me pertencem." |
| **Shell + módulos FE** | — (máquina) | Consomem a Access Layer que WRKS alimenta (sessão, empresa ativa, AccessDecision, navegação). Precondição de toda UI. |

## 4. MVP Scope (in) — telas, fluxos, formulários

1. **Login / OIDC callback** — redirect para Keycloak, retorno no callback, troca de code por
   sessão via `@journeyos/shared/auth-session`. Estados: `idle → redirecting → exchanging → authenticated | error`.
2. **Seleção de empresa** — lista das `usuario_empresa` ativas; cartão por empresa (nome, papel);
   `switchTo(empresaId)` emite novo JWT e popula `EmpresaContextService`. Auto-skip quando há só uma.
3. **Workspace dashboard** — visão geral da empresa ativa (dados, parâmetros, contagem de usuários,
   atalhos de administração conforme permissões).
4. **Workspace settings** — formulário de dados/parametros da empresa; org structure (CRUD leve de
   business units e teams).
5. **Gestão de usuários** — tabela de usuários da empresa; convite (form: e-mail + papel +
   `data_scope`); ativar/desativar; alterar papel (respeitando anti-escalonamento, INV-1 do BE).
6. **RBAC viewer** — papéis canônicos e o bundle de permissões de cada um (somente leitura no MVP).
7. **Troca de empresa em runtime** — disponível no Shell (topbar) a qualquer momento.

## 5. Out of Scope (MVP)

- Editor de papéis/permissões customizados (papéis são canônicos do grupo — apenas leitura).
- MFA/TOTP/WebAuthn (FE apenas reflete a flag `mfa-required`, sem fluxo de enrolamento).
- Self-service signup + billing.
- Tela de auditoria rica (a auditoria é consumo BE; viewer FE só se priorizado em wave tardia).
- UI de emergency access / API keys / risk score.
- Aprovação 2-step de convites; enforcement de restrição de IP.

## 6. Architectural Principles (FE)

1. **Standalone-first nas features** — toda feature e componente é `standalone`; `NgModule`
   **apenas** no `wrks.module.ts` (entry lazy).
2. **Signals-first** — estado de UI em `signal<T>` privado nas facades + `.asReadonly()` público;
   **sem NgRx** (ADR-002).
3. **Lazy-by-default** — Shell carrega WRKS via `loadChildren`; sub-rotas via `loadComponent`.
4. **OnPush mandatory** — todo componente usa `ChangeDetectionStrategy.OnPush`.
5. **A UI nunca decide acesso** — RBAC, sessão e empresa-context só via `@journeyos/shared/access-*`
   (`access-layer-contracts.md`). Zero `if (role === ...)` em features; zero `localStorage` direto.
6. **Multi-empresa via contexto único** — `EmpresaContextService` é a única fonte do `empresaId`
   ativo; troca cancela in-flight + invalida cache + re-avalia navegação (ADR-005).
7. **Padrão module-pattern** — slicing canônico de libs por módulo (ADR-001).

## 7. Success Signals

- **TTI do login** < 2 s em conexão típica; callback OIDC resolve sem flash de tela protegida.
- **Troca de empresa** reflete em toda a navegação em < 300 ms, **sem reload** e sem requisição da
  empresa anterior vazando para a nova.
- **p95** das chamadas de seleção de empresa / lista de usuários < 400 ms (cache quente BE).
- **Zero vazamento cross-empresa** na UI: nenhuma tela mostra dado de empresa diferente do
  `empresaId` ativo.
- **RBAC reflete em UI** em < 5 s após mudança de papel no BE (consistente com o success signal BE).
- **CLS** ~0 nas telas de admin (tabelas com skeleton via `ui-feedback`).
- 100% dos cenários do SPEC-08 viram spec Playwright descobrível (gate e2e-validate / A5).

---

## Referências

- ADRs: `adr/ADR-001..005`
- Brief: `../_brief.md`
- Blueprint FE: `02-architecture-blueprint.md`
- BE espelho: `docs/architecture/backend/services/wrks-service/01-architectural-vision.md`
- Access Layer: `docs/architecture/frontend/standards/access-layer-contracts.md`
