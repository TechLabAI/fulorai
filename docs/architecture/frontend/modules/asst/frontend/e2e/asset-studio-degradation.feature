# language: pt
Funcionalidade: Asset Studio — composição assistida e degradação graciosa
  Como Head de Growth
  Quero compor um rascunho com a IA a partir de um brief
  Para acelerar a produção sem depender da IA estar sempre disponível

  Contexto:
    Dado que o serviço de assets está disponível
    E que existe uma empresa ativa selecionada
    E um usuário "Marina" com permissão "asst.studio.compor"
    E um asset "Campanha Black Friday" no estado "RASCUNHO"

  Cenário: Composição bem-sucedida gera nova versão de rascunho
    Quando "Marina" abre o Asset Studio do asset
    E informa um brief "E-mail de oferta com urgência para Black Friday"
    E solicita a composição
    Então uma nova versão é criada no estado "RASCUNHO"
    E a versão tem origem "ASSET_STUDIO"
    E o brief de composição fica registrado na versão
    E a versão não é publicada automaticamente

  Cenário: IA indisponível degrada graciosamente
    Dado que a TechLab AI está indisponível
    Quando "Marina" solicita a composição no Asset Studio
    Então um aviso de indisponibilidade do Asset Studio é exibido
    E nenhuma versão é criada
    E a opção de "compor manualmente" é oferecida
    E o catálogo de assets continua acessível
    E o fluxo de aprovação continua funcionando

  Cenário: Asset Studio desligado por feature flag não afeta o resto
    Dado que a feature flag "asst.asset-studio" está desabilitada
    Quando "Marina" acessa o asset
    Então a ação de abrir o Asset Studio não é exibida
    E ela ainda pode criar uma versão manual
    E ela ainda pode submeter o asset para aprovação
