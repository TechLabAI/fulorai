# language: pt
Funcionalidade: Login e seleção de empresa
  Como usuário do Journey OS
  Quero entrar e escolher em qual empresa vou operar
  Para acessar o workspace correto sem recarregar o app

  Contexto:
    Dado que o serviço de identidade está disponível

  Cenário: Usuário com múltiplas empresas escolhe uma
    Dado um usuário autenticado com 2 empresas ativas
    Quando ele completa o login OIDC
    Então a tela de seleção de empresa é exibida com 2 opções
    Quando ele seleciona a empresa "Operação Rafael"
    Então um novo contexto de empresa é estabelecido
    E ele é redirecionado para "/wrks/workspace"
    E o dashboard exibe "Operação Rafael"

  Cenário: Usuário com uma única empresa pula a seleção
    Dado um usuário autenticado com exatamente 1 empresa ativa
    Quando ele completa o login OIDC
    Então ele é levado direto para "/wrks/workspace"
    E a tela de seleção de empresa não é exibida

  Cenário: Usuário sem empresa ativa
    Dado um usuário autenticado sem nenhuma empresa ativa
    Quando ele completa o login OIDC
    Então a página "sem acesso" é exibida
    E nenhuma rota protegida do workspace é acessível
