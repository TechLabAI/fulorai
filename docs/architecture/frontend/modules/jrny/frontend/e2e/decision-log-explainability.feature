# language: pt
Funcionalidade: Decision log explicável do roteamento
  Como SDR
  Quero entender por que um lead está em determinado estágio
  Para confiar na decisão e abordar bem

  Contexto:
    Dado que o serviço de jornadas está disponível
    E que existe uma empresa ativa selecionada
    E que "Lucas" tem permissão "jrny.roteamento.ler"

  Cenário: Ver estado de jornada e trilha de decisões do lead
    Dado um lead "lead-123" inscrito na jornada "Funil de Lançamento" no estágio "Oferta"
    Quando "Lucas" abre as decisões do lead "lead-123"
    Então o cartão de estado mostra o estágio corrente "Oferta" e a versão da jornada
    E a trilha lista as decisões da mais recente para a mais antiga
    E cada decisão mostra gatilho, regra, alvo, selo de assist e motivo

  Cenário: Decisão com assist de IA exibe selo de IA
    Dado uma decisão do lead com assist de IA "USADO"
    Quando "Lucas" abre as decisões do lead
    Então o selo da decisão indica que houve assist de IA

  Cenário: Decisão sem IA disponível exibe selo neutro, sem erro
    Dado uma decisão do lead com assist de IA "INDISPONIVEL"
    Quando "Lucas" abre as decisões do lead
    Então o selo exibido é "roteamento determinístico"
    E nenhum aviso de erro é exibido

  Cenário: Decisões SEM_MUDANCA e NAO_ROTEADO aparecem na trilha
    Dado um lead com decisões de resultado "SEM_MUDANCA" e "NAO_ROTEADO"
    Quando "Lucas" abre as decisões do lead
    Então ambas as decisões aparecem na trilha com seu motivo

  Cenário: Lead sem inscrição mostra estado vazio
    Dado um lead "lead-999" sem inscrição em jornada
    Quando "Lucas" abre as decisões do lead "lead-999"
    Então é exibido "Este lead ainda não entrou em nenhuma jornada."
