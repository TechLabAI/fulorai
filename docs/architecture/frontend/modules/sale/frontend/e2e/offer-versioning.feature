# language: pt
Funcionalidade: Catálogo de ofertas versionado
  Como infoprodutor
  Quero editar uma oferta gerando uma nova versão
  Para manter o histórico de preços imutável e auditável

  Contexto:
    Dado que o serviço de vendas está disponível
    E que existe uma empresa ativa selecionada
    E que "Rafael" tem permissão "sale.oferta.read", "sale.oferta.criar" e "sale.oferta.editar"

  Cenário: Listar e abrir uma oferta
    Quando "Rafael" navega para "/sale/offers"
    Então a lista de ofertas é exibida
    Quando ele abre a oferta "Plano Pro"
    Então o detalhe mostra a versão atual e as versões anteriores

  Cenário: Editar uma oferta cria nova versão
    Dado que "Rafael" abre a oferta "Plano Pro" na versão 1 com preço "1997.00"
    Quando ele edita o preço para "2497.00" e salva
    Então uma nova versão 2 da oferta é criada
    E a versão 1 permanece imutável na lista de versões

  Cenário: Editar oferta com preço inválido
    Dado que "Rafael" abre a oferta "Plano Pro"
    Quando ele edita o preço para "-10.00" e salva
    Então o sistema rejeita com "422 sale.oferta.preco-invalido"
    E uma mensagem inline é exibida no campo preço
    E nenhuma nova versão é criada
