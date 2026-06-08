# language: pt
Funcionalidade: Compra — breakdown de atribuição explicável + LTV
  Como infoprodutor
  Quero abrir uma compra e ver de onde veio cada real
  Para entender a receita de forma rastreável, nunca como total opaco

  Contexto:
    Dado que o serviço de vendas está disponível
    E que existe uma empresa ativa selecionada
    E que "Rafael" tem permissão "sale.compra.read" e "sale.atribuicao.read"

  Cenário: O FE não dispara registro de compra
    Quando "Rafael" navega para "/sale/purchases"
    Então a lista de compras é exibida
    E não existe ação de registrar nova compra na interface

  Cenário: Abrir o detalhe de uma compra com breakdown
    Dado uma compra "HOT-9981" confirmada de "1997.00" BRL
    Quando "Rafael" abre o detalhe da compra "HOT-9981"
    Então os itens da compra são exibidos
    E o breakdown de atribuição mostra cada touchpoint com tipo, valor e versão do modelo
    E a soma dos valores atribuídos é igual ao valor total da compra

  Cenário: Ver o LTV do contato da compra
    Dado uma compra "HOT-9981" do contato "rafael@acme.com"
    Quando "Rafael" abre o detalhe da compra "HOT-9981"
    Então o LTV do contato "rafael@acme.com" é exibido
