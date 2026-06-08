# language: pt
Funcionalidade: Deep-link para rotas do INTL
  Como usuário que recebe um link direto
  Quero abrir uma rota profunda do INTL e cair na tela certa
  Para acessar conteúdo específico sem navegar manualmente

  Contexto:
    Dado que estou autenticado com as permissões necessárias
    E que a empresa "Acme Cursos" está ativa

  Cenário: Deep-link para um nó de conhecimento resolve guards e breadcrumbs
    Quando abro diretamente "/intl/knowledge/no-123"
    Então os guards de autenticação, empresa e acesso são satisfeitos
    E a tela do nó "no-123" é exibida
    E o breadcrumb mostra "Inteligência ▸ Conhecimento ▸ <título do nó>"

  Cenário: Deep-link para uma conversa do copiloto
    Quando abro diretamente "/intl/copilot/c-001"
    Então a conversa "c-001" é carregada com seu histórico
    E o breadcrumb mostra "Inteligência ▸ Copilot ▸ <título da conversa>"

  Cenário: Deep-link sem empresa ativa força a seleção de empresa antes
    Dado que não há empresa ativa
    Quando abro diretamente "/intl/analytics"
    Então sou direcionado primeiro à seleção de empresa
    E após selecionar a empresa sou levado a "/intl/analytics"
