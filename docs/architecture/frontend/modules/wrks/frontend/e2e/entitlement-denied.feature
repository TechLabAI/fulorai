# language: pt
Funcionalidade: Acesso negado por entitlement (RBAC)
  Como SDR
  Quero ver apenas o que meu papel permite
  Para não acessar telas de administração que não me pertencem

  Contexto:
    Dado um usuário autenticado com papel "SDR"
    E uma empresa ativa como contexto

  Cenário: Menu não exibe itens de administração
    Quando o Shell deriva a navegação
    Então o menu não exibe "Usuários"
    E o menu não exibe "Papéis"
    E o menu não exibe "Configurações"

  Cenário: Acesso direto a rota de administração é bloqueado
    Quando ele tenta acessar "/wrks/users" diretamente
    Então o guard de acesso nega a navegação
    E ele permanece em uma rota permitida pelo seu papel
