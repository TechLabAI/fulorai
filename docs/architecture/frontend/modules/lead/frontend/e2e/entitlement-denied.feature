# language: pt
Funcionalidade: Restrição de ações por permissão (RBAC) no LEAD
  Como plataforma do Journey OS
  Quero ocultar ações e deep links sem permissão
  Para que cada persona veja apenas o que pode usar

  Contexto:
    Dado que o serviço de leads está disponível
    E que existe uma empresa ativa selecionada

  Cenário: SDR sem permissões de governança não vê ações restritas
    Dado um usuário "Lucas" com papel "SDR" e apenas "lead.lead.read"
    Quando ele abre o módulo de leads
    Então ele vê a fila e o detalhe dos leads
    Mas ele não vê o deep link "Regras"
    E ele não vê a ação de criar ou editar segmentos
    E ele não vê a ação "Requalificar" no detalhe do lead

  Cenário: Head de Growth vê as ações de governança
    Dado um usuário "Marina" com papel "HEAD_GROWTH" e permissões de governança
    Quando ela abre o módulo de leads
    Então ela vê os deep links "Regras", "Segmentos", "Surveys" e "Maturity Score"
