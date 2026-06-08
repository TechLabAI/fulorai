# language: pt
Funcionalidade: Pipeline Kanban — mover oportunidade de estágio
  Como SDR/closer
  Quero arrastar uma oportunidade para o próximo estágio no Kanban
  Para avançar o funil de forma rápida e com leitura imediata

  Contexto:
    Dado que o serviço de vendas está disponível
    E que existe uma empresa ativa selecionada
    E que "Lucas" tem permissão "sale.oportunidade.read" e "sale.oportunidade.mover"

  Cenário: Acesso à raiz redireciona para o pipeline
    Quando "Lucas" navega para "/sale"
    Então o sistema redireciona para "/sale/pipeline"

  Cenário: Abrir o pipeline carregado de forma lazy
    Quando "Lucas" navega para "/sale/pipeline"
    Então o board Kanban é exibido com colunas por estágio
    E cada coluna mostra a contagem e a soma de valor das oportunidades

  Cenário: Mover oportunidade ao próximo estágio com atualização otimista
    Dado um pipeline com a oportunidade "Plano Pro - Acme" no estágio "NOVA"
    Quando "Lucas" arrasta a oportunidade "Plano Pro - Acme" para a coluna "CONTATO"
    Então o card aparece imediatamente na coluna "CONTATO"
    E o sistema persiste o novo estágio via PATCH
    E o histórico de estágio registra a transição

  Cenário: Rollback do move otimista quando a oportunidade já está fechada
    Dado um pipeline com a oportunidade "Mentoria - Beta" já "GANHA"
    Quando "Lucas" tenta arrastar a oportunidade "Mentoria - Beta" para outra coluna
    Então o sistema rejeita com "409 sale.oportunidade.ja-fechada"
    E o card volta para a coluna de origem
    E um toast de erro é exibido
