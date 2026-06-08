# SPEC-08 — E2E Scenarios — COMM · Frontend

> Cenários e2e (Gherkin pt-BR). Cada arquivo vira um `.feature` em `e2e/` e um spec stub em
> `apps/comm-e2e/` (gerado pelo `@journeyos/internal:module`). Execução real dos fluxos = `/fe-implement` P9.
> Cada cláusula SHALL (EARS) das SPEC-01..07 tem cenário correspondente aqui.

## Inventário de features e2e → cláusulas EARS cobertas

| `.feature` | Fluxo | Cláusulas cobertas |
|---|---|---|
| `message-dispatch-tracking.feature` | Golden path: disparar + rastrear ciclo de vida (polling) | C-01.6, C-02.5, C-03.4, C-04.3, C-04.5, C-06.4 |
| `dispatch-idempotency.feature` | Duplo clique / replay = 1 envio | C-04.3, C-04.4 |
| `template-authoring-and-activation.feature` | Criar RASCUNHO → editar (placeholders) → ativar/arquivar | C-02.3, C-03.2, C-03.3, C-03.5, C-07.x |
| `template-studio-degradation.feature` | Studio compõe; 503 degrada gracioso; flag off | C-02.4, C-05.3, C-07.3 |
| `routing-resolution.feature` | Canal preferido → fallback; sem-canal | C-07.4 |
| `channel-config-security.feature` | Config de canal sem expor segredo; duplicado | C-02.6, C-04.6, C-07.5 |
| `empresa-switch-isolation.feature` | Troca de empresa invalida estado + para polling | C-04.7, C-06.3 |
| `entitlement-denied.feature` | Acesso/ação sem permissão `comm.*` | C-01.5, C-05.5 |
| `deep-link.feature` | Acesso direto por URL respeitando guards | C-01.2, C-01.3, C-01.4, C-06.2 |

## Resumo dos cenários (detalhe nos `.feature`)

1. **message-dispatch-tracking** — disparo de template ATIVO; `202 ENFILEIRADA`; timeline evolui
   `ENVIADA → ENTREGUE → LIDA` por polling; polling encerra no terminal.
2. **dispatch-idempotency** — duplo clique em "Enviar" / replay com a mesma `Idempotency-Key` produz
   uma única mensagem.
3. **template-authoring-and-activation** — criar template RASCUNHO; editar corpo com `{{nome}}`;
   validação de placeholder não declarado; assunto obrigatório p/ EMAIL; ativar; arquivar.
4. **template-studio-degradation** — compor via Studio gera rascunho; IA indisponível degrada
   (corpo inalterado, CTA manual); flag `comm.template-studio` off oculta o Studio.
5. **routing-resolution** — regra resolve WhatsApp (preferido) e cai para e-mail (fallback);
   sem canal resolvível → erro orientativo.
6. **channel-config-security** — configurar canal guarda só `credencialRef` (mascarada); config
   duplicada (canal, provedor) é rejeitada.
7. **empresa-switch-isolation** — trocar de empresa limpa catálogo/mensagens e encerra polling; sem
   vazamento cross-empresa.
8. **entitlement-denied** — usuário sem `comm.mensagem.enviar` não vê/não executa o disparo; rota sem
   permissão → "sem permissão".
9. **deep-link** — acesso direto a `/comm/messages/:id` autentica, exige empresa e permissão antes de
   renderizar.

## Critério de aceite (EARS)

- **C-08.1 (Ubiquitous):** `THE SYSTEM SHALL manter cada cláusula SHALL das SPEC-01 a 07 mapeada para ao menos um cenário Gherkin em e2e`
- **C-08.2 (Ubiquitous):** `THE SYSTEM SHALL gerar um spec Playwright descobrível em apps/comm-e2e para cada feature declarada no generator-config`

## Referências

- `e2e/*.feature` (Gherkin) · `generator-config.yml` (`e2e.features`)
- SPEC-01..07 (cláusulas EARS) · gate `/fe-architect-specs-validate`
