# language: pt
Funcionalidade: Negação de acesso por entitlement
  Como operação do Journey OS
  Quero que rotas e ações sem permissão sejam escondidas ou negadas
  Para que o RBAC seja respeitado na UI

  Contexto:
    Dado que o serviço de jornadas está disponível
    E que existe uma empresa ativa selecionada

  Cenário: Sem permissão de leitura, a rota é negada
    Dado que "Lucas" não tem a permissão "jrny.jornada.ler"
    Quando ele tenta acessar "/jrny/journeys"
    Então a ativação da rota é negada pelo accessGuard
    E o item de menu "Jornadas" não é exibido

  Cenário: Sem permissão de publicação, a ação fica oculta
    Dado que "Marina" tem "jrny.jornada.editar" mas não "jrny.jornada.publicar"
    Quando ela abre o builder de um rascunho
    Então a ação de publicar não é exibida

  Cenário: Sem permissão de criar regra, o editor de regra fica oculto
    Dado que "Lucas" tem "jrny.roteamento.ler" mas não "jrny.regra.criar"
    Quando ele abre as regras de uma jornada
    Então a ação de criar regra não é exibida
