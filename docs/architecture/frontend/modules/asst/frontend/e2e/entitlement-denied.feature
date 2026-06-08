# language: pt
Funcionalidade: Visibilidade de ações por permissão (RBAC)
  Como plataforma com RBAC
  Quero que a UI só exiba ações permitidas ao usuário
  Para que a decisão de acesso venha sempre do AccessDecision (nunca da UI)

  Contexto:
    Dado que o serviço de assets está disponível
    E que existe uma empresa ativa selecionada

  Cenário: SDR sem permissões de autoria só vê leitura
    Dado um usuário "Lucas" com permissão "asst.asset.ler" apenas
    Quando ele abre o catálogo de assets
    Então ele vê os assets publicados
    Mas a ação "Novo asset" não é exibida
    E a ação "Aprovar" não é exibida
    E a ação "Publicar" não é exibida
    E o deep link "Aprovações" não aparece no menu

  Cenário: Autor sem permissão de aprovação não acessa a fila
    Dado um usuário "Marina" sem a permissão "asst.asset.aprovar"
    Quando ela tenta acessar "/asst/approvals" por deep link
    Então o acesso é bloqueado pelo guard de permissão

  Cenário: Composição indisponível sem permissão de Studio
    Dado um usuário "Lucas" sem a permissão "asst.studio.compor"
    Quando ele abre um asset
    Então a ação de abrir o Asset Studio não é exibida
