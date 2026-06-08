# language: pt
Funcionalidade: Isolamento multi-empresa na troca de contexto
  Como usuário que opera mais de uma empresa
  Quero que trocar de empresa limpe o estado da empresa anterior
  Para nunca ver dados de uma empresa no contexto de outra

  Contexto:
    Dado que estou autenticado e opero as empresas "Acme Cursos" e "Beta Academy"
    E que a empresa "Acme Cursos" está ativa

  Cenário: Troca de empresa limpa a conversa corrente do copiloto
    Dado que estou numa conversa em "/intl/copilot" com mensagens da "Acme Cursos"
    Quando troco a empresa ativa para "Beta Academy" pela topbar
    Então a conversa da "Acme Cursos" não aparece mais
    E nenhuma mensagem da empresa anterior é exibida

  Cenário: Pergunta em andamento é cancelada ao trocar de empresa
    Dado que enviei uma pergunta e a resposta está "pensando"
    Quando troco a empresa ativa para "Beta Academy"
    Então a pergunta em andamento é cancelada
    E nenhuma resposta da "Acme Cursos" é renderizada na "Beta Academy"

  Cenário: Knowledge e Analytics recarregam no novo escopo
    Dado que estou em "/intl/knowledge" vendo nós da "Acme Cursos"
    Quando troco a empresa ativa para "Beta Academy"
    Então a lista de nós é recarregada para "Beta Academy"
    E nenhum nó da "Acme Cursos" permanece visível
