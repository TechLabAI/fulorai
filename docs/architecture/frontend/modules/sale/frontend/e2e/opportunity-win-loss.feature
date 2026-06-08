# language: pt
Funcionalidade: Detalhe da oportunidade — ganhar e perder
  Como SDR/closer
  Quero registrar o ganho ou a perda de uma oportunidade
  Para fechar o deal com motivo rastreável e estado terminal

  Contexto:
    Dado que o serviço de vendas está disponível
    E que existe uma empresa ativa selecionada
    E que "Lucas" tem permissão "sale.oportunidade.read" e "sale.oportunidade.fechar"

  Cenário: Ganhar uma oportunidade aberta
    Dado que "Lucas" abre a oportunidade "Plano Pro - Acme" no estado "EM_ANDAMENTO"
    Quando ele marca a oportunidade como ganha
    Então o estado da oportunidade passa a "GANHA"
    E as ações de ganhar e perder ficam desabilitadas

  Cenário: Perder uma oportunidade exige motivo
    Dado que "Lucas" abre a oportunidade "Mentoria - Beta" no estado "EM_ANDAMENTO"
    Quando ele tenta marcar como perdida sem informar o motivo
    Então o sistema rejeita com "422 sale.oportunidade.motivo-obrigatorio"
    E uma mensagem inline é exibida no campo motivo
    E a oportunidade não é fechada

  Cenário: Perder uma oportunidade com motivo
    Dado que "Lucas" abre a oportunidade "Mentoria - Beta" no estado "EM_ANDAMENTO"
    Quando ele marca como perdida com o motivo "Sem orçamento"
    Então o estado da oportunidade passa a "PERDIDA"

  Cenário: Oportunidade fechada é terminal
    Dado que "Lucas" abre a oportunidade "Plano Pro - Acme" já "GANHA"
    Então as ações de ganhar e perder estão desabilitadas
    E o card da oportunidade não é arrastável no pipeline
