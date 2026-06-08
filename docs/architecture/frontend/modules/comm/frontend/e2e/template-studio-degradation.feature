# language: pt
Funcionalidade: Template Studio — composição assistida e degradação graciosa
  Como Head de Growth
  Quero compor a copy de uma mensagem com a IA a partir de um brief
  Para acelerar a produção sem depender da IA estar sempre disponível

  Contexto:
    Dado que o serviço de comunicação está disponível
    E que existe uma empresa ativa selecionada
    E um usuário "Marina" com permissão "comm.studio.compor"
    E um template "Boas-vindas" no estado "RASCUNHO"

  Cenário: Composição bem-sucedida preenche um rascunho para revisão
    Quando "Marina" abre o Template Studio do template
    E informa um brief "Mensagem de boas-vindas calorosa para novos leads"
    E solicita a composição
    Então um novo corpo é proposto no estado "RASCUNHO"
    E o template não é ativado automaticamente
    E "Marina" pode revisar antes de aceitar o rascunho

  Cenário: IA indisponível degrada graciosamente
    Dado que a IA está indisponível
    Quando "Marina" solicita a composição no Template Studio
    Então um aviso de indisponibilidade do Studio é exibido
    E o corpo do template permanece inalterado
    E a opção de "editar manualmente" é oferecida
    E o catálogo, o roteamento e o disparo continuam funcionando

  Cenário: Studio desligado por feature flag não afeta o resto
    Dado que a feature flag "comm.template-studio" está desabilitada
    Quando "Marina" acessa o template
    Então a ação de abrir o Template Studio não é exibida
    E ela ainda pode editar o corpo manualmente
    E ela ainda pode ativar o template
