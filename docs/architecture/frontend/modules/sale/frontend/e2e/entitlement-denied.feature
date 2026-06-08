# language: pt
Funcionalidade: Negação de acesso no SALE
  Como usuário sem permissão
  Quero que rotas e ações sem permissão sejam negadas e escondidas
  Para que a UI reflita o RBAC efetivo (decidido pela Access Layer)

  Contexto:
    Dado que o serviço de vendas está disponível
    E que existe uma empresa ativa selecionada

  Cenário: Rota negada sem permissão
    Dado que "Visitante" não tem a permissão "sale.oportunidade.read"
    Quando "Visitante" tenta acessar "/sale/pipeline"
    Então o accessGuard nega a ativação da rota
    E o deep link "Pipeline" não aparece no menu

  Cenário: Ação escondida sem permissão de fechamento
    Dado que "Lucas" tem "sale.oportunidade.read" mas não "sale.oportunidade.fechar"
    Quando "Lucas" abre uma oportunidade
    Então as ações de ganhar e perder não são exibidas

  Cenário: Deep link de receita escondido sem permissão
    Dado que "Lucas" não tem a permissão "sale.ltv.read"
    Então o deep link "Receita" não aparece no menu
