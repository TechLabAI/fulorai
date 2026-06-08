# language: pt
Funcionalidade: Deep-link e feature flags
  Como operação do Journey OS
  Quero acessar telas do JRNY diretamente por URL
  Para retomar o trabalho a partir de links contextuais

  Contexto:
    Dado que o serviço de jornadas está disponível
    E que existe uma empresa ativa selecionada
    E que o usuário tem permissão "jrny.jornada.ler" e "jrny.roteamento.ler"

  Cenário: Deep-link direto ao builder de uma jornada
    Quando o usuário acessa "/jrny/journeys/abc/builder" diretamente
    Então o builder da jornada "abc" é carregado de forma lazy

  Cenário: Deep-link direto às decisões de um lead
    Quando o usuário acessa "/jrny/leads/lead-123/decisions" diretamente
    Então a trilha de decisões do lead "lead-123" é exibida

  Cenário: Deep-link a jornada inexistente mostra estado vazio
    Quando o usuário acessa "/jrny/journeys/inexistente/builder"
    Então é exibido "Jornada não encontrada."

  Cenário: Analytics desabilitada por flag omite a rota
    Dado que a flag "jrny.journey-analytics" está desabilitada
    Quando o usuário acessa "/jrny/analytics" diretamente
    Então a rota é omitida e o item de menu "Analytics" não é exibido
