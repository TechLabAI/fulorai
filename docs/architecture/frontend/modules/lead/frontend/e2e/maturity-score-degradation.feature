# language: pt
Funcionalidade: Degradação graciosa do assist de IA no Maturity Score
  Como operação do Journey OS
  Quero que a indisponibilidade da IA não quebre a leitura do score
  Para continuar priorizando com o score determinístico

  Contexto:
    Dado que o serviço de leads está disponível
    E que existe uma empresa ativa selecionada

  Cenário: Score determinístico exibe selo neutro, sem erro
    Dado um lead "Carla Dias" cujo último score foi calculado sem assist de IA
    Quando "Lucas" abre o detalhe do lead
    Então o selo exibido é "score determinístico"
    E nenhum aviso de erro é exibido
    E o breakdown das 6 dimensões continua disponível

  Cenário: Assist de IA presente exibe selo de IA
    Dado um lead "Ana Souza" cujo score foi calculado com assist de IA
    Quando "Lucas" abre o detalhe do lead
    Então o selo exibido indica que houve assist de IA
