# language: pt
Funcionalidade: Isolamento por empresa na troca de contexto
  Como operação multi-empresa
  Quero que trocar de empresa nunca mostre jornadas de outra empresa
  Para garantir isolamento de dados entre tenants

  Contexto:
    Dado que o serviço de jornadas está disponível

  Cenário: Trocar de empresa invalida a lista de jornadas em tela
    Dado que "Marina" está na empresa "Acme" vendo a jornada "Funil Acme"
    Quando ela troca para a empresa "Globex"
    Então a lista de jornadas é invalidada antes de carregar
    E nenhuma jornada da empresa "Acme" permanece visível
    E apenas jornadas da empresa "Globex" são exibidas

  Cenário: Trocar de empresa com o builder aberto descarta a jornada em edição
    Dado que "Marina" está editando um rascunho na empresa "Acme"
    Quando ela troca para a empresa "Globex"
    Então o builder é fechado e o estado de edição é descartado
