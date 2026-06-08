# language: pt
Funcionalidade: Captura de respostas de survey enriquece o perfil
  Como Head de Growth do Journey OS
  Quero definir surveys e capturar respostas por lead
  Para enriquecer o perfil e disparar o recálculo do score

  Contexto:
    Dado que o serviço de leads está disponível
    E que existe uma empresa ativa selecionada
    E um usuário "Marina" com permissões "lead.survey.read", "lead.survey.criar" e "lead.survey.responder"

  Cenário: Responder survey atualiza o perfil e recalcula o score
    Dado um survey "Diagnóstico inicial" com perguntas definidas
    Quando "Marina" responde o survey para o lead "Ana Souza"
    Então os atributos do perfil com origem "SURVEY" são atualizados
    E o Maturity Score do lead é recalculado

  Cenário: Resposta com pergunta inválida é rejeitada
    Quando "Marina" envia uma resposta que referencia uma pergunta inválida
    Então um erro de campo na resposta é exibido
    E o diálogo de resposta permanece aberto
