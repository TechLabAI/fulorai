# language: pt
Funcionalidade: Isolamento multi-empresa do catálogo de assets
  Como plataforma multi-tenant
  Quero que assets nunca vazem entre empresas
  Para preservar o isolamento por empresa (LGPD)

  Contexto:
    Dado que o serviço de assets está disponível
    E um usuário autenticado com acesso às empresas "Operação A" e "Operação B"

  Cenário: Catálogo reflete apenas a empresa ativa
    Dado que a empresa ativa é "Operação A"
    Quando o usuário abre o catálogo de assets
    Então apenas assets da "Operação A" são exibidos

  Cenário: Troca de empresa invalida o catálogo anterior
    Dado que a empresa ativa é "Operação A" com o catálogo carregado
    Quando o usuário troca para a empresa "Operação B"
    Então o catálogo da "Operação A" é invalidado antes de renderizar
    E nenhum asset da "Operação A" aparece sob a "Operação B"
    E o catálogo passa a exibir apenas assets da "Operação B"

  Cenário: Detalhe de asset de outra empresa não é acessível
    Dado que a empresa ativa é "Operação B"
    Quando o usuário tenta abrir por deep link um asset da "Operação A"
    Então o asset não é encontrado no contexto da "Operação B"
