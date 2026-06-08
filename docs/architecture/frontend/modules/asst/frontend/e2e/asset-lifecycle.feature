# language: pt
Funcionalidade: Ciclo de vida do asset (criar → versão → submeter → aprovar → publicar)
  Como time de conteúdo do Journey OS
  Quero criar, versionar, aprovar e publicar um asset
  Para ter uma versão vigente confiável e reutilizável

  Contexto:
    Dado que o serviço de assets está disponível
    E que existe uma empresa ativa selecionada

  Cenário: Golden path — criar, versionar e publicar um e-mail
    Dado um usuário "Marina" com permissões de autoria de asset
    Quando ela cria um asset do tipo "EMAIL" com título "Boas-vindas"
    Então o asset é criado no estado "RASCUNHO" sem versão vigente
    Quando ela cria uma versão manual com conteúdo de boas-vindas
    Então a versão 1 é criada com origem "MANUAL" no estado "RASCUNHO"
    Quando ela submete o asset para aprovação
    Então o asset passa para o estado "EM_REVISAO"
    Dado um usuário "Rafael" com permissão de aprovação e publicação
    Quando ele aprova o asset "Boas-vindas"
    Então o asset passa para o estado "APROVADO"
    Quando ele publica o asset
    Então o asset passa para o estado "PUBLICADO"
    E a versão vigente do asset é a versão 1

  Cenário: Versão publicada é imutável
    Dado um asset "Boas-vindas" no estado "PUBLICADO" com versão vigente 1
    Quando "Marina" abre a versão 1 publicada
    Então a edição de conteúdo da versão 1 não é oferecida
    E a única ação de alteração disponível é "criar nova versão"

  Cenário: Publicar uma nova versão atualiza a versão vigente
    Dado um asset "Boas-vindas" no estado "PUBLICADO" com versão vigente 1
    Quando "Marina" cria a versão 2 e a submete
    E "Rafael" aprova e publica a versão 2
    Então a versão vigente do asset passa a ser a versão 2
    E a versão 1 continua existindo no histórico
