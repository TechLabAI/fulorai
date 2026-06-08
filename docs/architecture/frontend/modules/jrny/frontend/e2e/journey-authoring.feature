# language: pt
Funcionalidade: Autoria de jornada (criar, montar estágios, publicar)
  Como Head de Growth
  Quero desenhar uma jornada multi-estágio e publicá-la
  Para orquestrar o funil de forma explícita e governável

  Contexto:
    Dado que o serviço de jornadas está disponível
    E que existe uma empresa ativa selecionada
    E que "Marina" tem permissão "jrny.jornada.criar" e "jrny.estagio.criar"

  Cenário: Acesso à raiz redireciona para a lista de jornadas
    Quando "Marina" navega para "/jrny"
    Então o sistema redireciona para "/jrny/journeys"

  Cenário: Criar um rascunho de jornada
    Dado que "Marina" está na lista de jornadas
    Quando ela cria a jornada "Funil de Lançamento"
    Então a jornada aparece com estado "RASCUNHO" e versão 1
    E o builder da jornada é aberto

  Cenário: Adicionar e reordenar estágios no builder
    Dado um rascunho "Funil de Lançamento" sem estágios
    Quando "Marina" adiciona os estágios "Captura", "Nutrição" e "Oferta"
    E reordena "Oferta" para antes de "Nutrição" usando o teclado
    Então a ordem dos estágios reflete a nova sequência
    E cada estágio expõe um nome acessível para leitores de tela

  Cenário: Publicar uma jornada com ao menos um estágio
    Dado um rascunho "Funil de Lançamento" com 3 estágios
    E que "Rafael" tem permissão "jrny.jornada.publicar"
    Quando "Rafael" publica a jornada
    Então o estado da jornada passa a "PUBLICADA"
    E o builder passa a ser somente leitura
