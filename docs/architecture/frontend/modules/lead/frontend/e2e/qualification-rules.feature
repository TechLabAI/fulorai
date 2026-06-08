# language: pt
Funcionalidade: Governança de regras de qualificação versionadas
  Como Head de Growth do Journey OS
  Quero versionar e ativar regras de qualificação
  Para controlar como o Maturity Score é calculado de forma rastreável

  Contexto:
    Dado que o serviço de leads está disponível
    E que existe uma empresa ativa selecionada
    E um usuário "Marina" com permissões "lead.qualification.read", "lead.qualification.criar" e "lead.qualification.ativar"

  Cenário: Criar versão inativa e ativá-la
    Quando "Marina" cria uma nova versão de regra
    Então a nova versão é criada no estado inativa
    Quando ela ativa a nova versão
    Então a nova versão passa a ser a versão ativa
    E a versão ativa anterior é desativada

  Cenário: Requalificar sem regra ativa é bloqueado
    Dado que nenhuma regra de qualificação está ativa
    Quando "Lucas" abre um lead e tenta "Requalificar"
    Então a ação "Requalificar" está desabilitada
    E um aviso para ativar uma regra é exibido
