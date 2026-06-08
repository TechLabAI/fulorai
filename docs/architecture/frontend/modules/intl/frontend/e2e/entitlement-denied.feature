# language: pt
Funcionalidade: Controle de acesso — UI ausente por decisão de acesso
  Como Lucas (SDR) com acesso restrito
  Quero que apenas as telas que meu papel permite estejam visíveis
  Para não ver áreas que não me pertencem

  Contexto:
    Dado que estou autenticado como "SDR"
    E que a empresa "Acme Cursos" está ativa

  Cenário: Item de menu oculto sem permissão de analítica
    Dado que não tenho a permissão "intl.analytics.read"
    Quando abro o menu de "Inteligência"
    Então não vejo o item "Analítica"
    Mas vejo o item "Copilot"

  Cenário: Acesso direto a rota negada é bloqueado
    Dado que não tenho a permissão "intl.analytics.read"
    Quando tento abrir "/intl/analytics" diretamente
    Então sou impedido de acessar a tela
    E sou redirecionado para uma rota permitida

  Cenário: Permissão revogada em runtime
    Dado que estou em "/intl/knowledge" com "intl.knowledge.write"
    Quando minha permissão de escrita é revogada durante a sessão
    Então as ações de criar/indexar/arquivar deixam de estar disponíveis
    E vejo um aviso de que não tenho mais permissão para escrever
