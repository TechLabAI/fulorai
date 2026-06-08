# language: pt
Funcionalidade: Deep links do LEAD respeitam guards
  Como plataforma do Journey OS
  Quero que o acesso direto a rotas respeite sessão e permissão
  Para proteger as rotas independentemente da navegação pelo menu

  Contexto:
    Dado que o serviço de leads está disponível

  Cenário: Acesso direto sem sessão redireciona para login
    Dado que não há sessão ativa
    Quando o usuário acessa diretamente "/lead/leads/123"
    Então ele é redirecionado para o login

  Cenário: Acesso direto sem permissão é bloqueado
    Dado um usuário autenticado com empresa ativa, sem "lead.qualification.read"
    Quando ele acessa diretamente "/lead/qualification"
    Então o acesso é bloqueado pelo guard de permissão
