# SPEC-08 — E2E Scenarios — WRKS

> Cenários Gherkin. Cada bloco vira um `.feature` em `../e2e/` e é copiado para
> `apps/wrks-e2e/src/specs/` pelo gerador e2e. Execução real dos fluxos = wave P9 do implement;
> aqui o gate (A5) só verifica descoberta/compilação.

## Arquivos

| Feature file | Cenário | Tipo |
|---|---|---|
| `login-and-empresa-select.feature` | login OIDC → seleção de empresa → dashboard | golden path |
| `user-administration.feature` | convidar usuário + alterar papel (+ anti-escalonamento) | happy + business rule |
| `empresa-switch-isolation.feature` | trocar de empresa sem vazamento cross-empresa | isolamento (LGPD) |
| `entitlement-denied.feature` | SDR não vê telas de administração | entitlement |
| `deep-link.feature` | deep link `/wrks/users` respeita guard/permissão | deep link |

## Resumo dos cenários

### login-and-empresa-select (golden path)
- Dado um usuário com 2 empresas ativas, quando ele faz login, então vê a tela de seleção de empresa.
- Quando seleciona uma empresa, então recebe novo contexto e é levado ao dashboard do workspace.
- Dado um usuário com exatamente 1 empresa, quando faz login, então vai direto ao dashboard (auto-skip).

### user-administration
- Dado um `INFOPRODUTOR` na tela de usuários, quando convida `novo@empresa.com` como `SDR`, então o
  usuário aparece como `convidado`.
- Quando tenta atribuir papel acima do seu, então vê erro de escalonamento e a operação é rejeitada.

### empresa-switch-isolation
- Dado um usuário operando a empresa A com a lista de usuários carregada, quando troca para a empresa
  B, então nenhum dado da empresa A permanece visível e a lista recarrega no escopo de B.

### entitlement-denied
- Dado um `SDR` autenticado, então o menu não exibe "Usuários"/"Papéis"/"Configurações" e o acesso
  direto a `/wrks/users` é negado pelo guard.

### deep-link
- Dado um `INFOPRODUTOR` com sessão e empresa ativas, quando acessa `/wrks/users` diretamente, então a
  página carrega; sem sessão, é redirecionado ao login preservando `returnUrl`.
