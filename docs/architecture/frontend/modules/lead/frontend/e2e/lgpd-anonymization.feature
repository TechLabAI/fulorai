# language: pt
Funcionalidade: Anonimização LGPD de um lead
  Como operação do Journey OS responsável por privacidade
  Quero anonimizar um lead com confirmação explícita
  Para cumprir a LGPD e travar edições sobre dados anonimizados

  Contexto:
    Dado que o serviço de leads está disponível
    E que existe uma empresa ativa selecionada
    E um usuário "Marina" com permissão "lead.lead.anonimizar"

  Cenário: Anonimizar exige confirmação e trava edições
    Dado um lead "Bruno Lima" no estado "EM_QUALIFICACAO"
    Quando "Marina" solicita anonimizar o lead
    Então um modal de confirmação é exibido antes da chamada
    Quando ela confirma a anonimização
    Então o lead passa para o estado "ANONIMIZADO"
    E os dados pessoais do lead são suprimidos na tela
    E as ações "Editar perfil" e "Requalificar" ficam desabilitadas

  Cenário: Editar um lead anonimizado é bloqueado
    Dado um lead "Bruno Lima" no estado "ANONIMIZADO"
    Quando "Marina" abre o detalhe do lead
    Então um aviso de lead anonimizado é exibido
    E a edição de perfil não é oferecida
