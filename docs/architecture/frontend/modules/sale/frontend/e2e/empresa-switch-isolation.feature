# language: pt
Funcionalidade: Isolamento por empresa no SALE
  Como usuário multi-empresa
  Quero que trocar de empresa invalide o pipeline e as listas em tela
  Para nunca ver dados de outra empresa (LGPD)

  Contexto:
    Dado que o serviço de vendas está disponível
    E que "Lucas" tem permissão "sale.oportunidade.read"
    E que existe a empresa "Acme" e a empresa "Beta"

  Cenário: Trocar de empresa invalida o pipeline em tela
    Dado que "Lucas" está no pipeline com a empresa "Acme" ativa
    E que o board mostra oportunidades da empresa "Acme"
    Quando "Lucas" troca a empresa ativa para "Beta"
    Então o pipeline da empresa "Acme" é invalidado
    E o sistema carrega o pipeline da empresa "Beta"

  Cenário: Trocar de empresa invalida a lista de compras em tela
    Dado que "Lucas" está na lista de compras com a empresa "Acme" ativa
    Quando "Lucas" troca a empresa ativa para "Beta"
    Então a lista de compras da empresa "Acme" é invalidada antes de carregar a de "Beta"
