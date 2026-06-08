# language: pt
Funcionalidade: Deep link com guarda de sessão e empresa
  Como usuário do Journey OS
  Quero acessar uma rota profunda diretamente
  Para chegar onde preciso, respeitando autenticação e contexto

  Cenário: Deep link permitido com sessão e empresa ativas
    Dado um usuário autenticado com papel "INFOPRODUTOR"
    E uma empresa ativa como contexto
    Quando ele acessa "/wrks/users" diretamente
    Então a página de usuários é carregada

  Cenário: Deep link sem sessão redireciona ao login
    Dado um usuário não autenticado
    Quando ele acessa "/wrks/users" diretamente
    Então ele é redirecionado para "/login"
    E após autenticar é levado de volta para "/wrks/users"

  Cenário: Deep link autenticado sem empresa exige seleção
    Dado um usuário autenticado sem empresa ativa selecionada
    Quando ele acessa "/wrks/users" diretamente
    Então ele é redirecionado para "/empresa-select"
