# language: pt
Funcionalidade: Deep links do ASST respeitam guards
  Como usuário que recebe um link direto
  Quero acessar uma rota interna do ASST
  Para cair na tela certa só quando autenticado, com empresa ativa e permissão

  Contexto:
    Dado que o serviço de assets está disponível

  Cenário: Deep link sem sessão redireciona para login
    Dado um usuário não autenticado
    Quando ele acessa diretamente "/asst/assets/123"
    Então ele é redirecionado para o login
    E após autenticar e selecionar empresa, ele retorna para "/asst/assets/123"

  Cenário: Deep link válido abre o detalhe do asset
    Dado um usuário autenticado com empresa ativa e permissão "asst.asset.ler"
    Quando ele acessa diretamente "/asst/assets/123"
    Então o detalhe do asset 123 é exibido com seu histórico de versões

  Cenário: Deep link para aprovações exige permissão
    Dado um usuário autenticado com empresa ativa sem "asst.asset.aprovar"
    Quando ele acessa diretamente "/asst/approvals"
    Então o acesso é bloqueado pelo guard de permissão

  Cenário: Deep link para asset inexistente mostra não encontrado
    Dado um usuário autenticado com empresa ativa e permissão "asst.asset.ler"
    Quando ele acessa diretamente "/asst/assets/inexistente"
    Então o estado "asset não encontrado" é exibido
