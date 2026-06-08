# language: pt
Funcionalidade: Acesso por deep link respeitando os guards
  Como usuário
  Quero acessar uma URL direta do COMM
  Para abrir uma mensagem ou tela específica respeitando autenticação, empresa e permissão

  Contexto:
    Dado que o serviço de comunicação está disponível

  Cenário: Deep link sem sessão redireciona ao login
    Dado um usuário não autenticado
    Quando ele acessa diretamente "/comm/messages/abc-123"
    Então ele é redirecionado para o login
    E a tela de mensagem não é renderizada

  Cenário: Deep link sem empresa ativa leva à seleção de empresa
    Dado um usuário autenticado sem empresa ativa
    Quando ele acessa diretamente "/comm/templates"
    Então ele é levado à seleção de empresa

  Cenário: Deep link válido abre a tela com contexto resolvido
    Dado um usuário "Lucas" autenticado, com empresa ativa e permissão "comm.mensagem.ler"
    Quando ele acessa diretamente "/comm/messages/abc-123"
    Então o detalhe da mensagem "abc-123" é carregado
    E o breadcrumb "Comunicação ▸ Mensagens" é exibido

  Cenário: Redirecionamento da raiz do módulo
    Dado um usuário "Lucas" autenticado com empresa ativa
    Quando ele acessa "/comm"
    Então ele é redirecionado para "/comm/templates"
