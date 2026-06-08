# language: pt
Funcionalidade: Guardas de publicação e imutabilidade da jornada
  Como operação do Journey OS
  Quero que jornadas publicadas sejam imutáveis e a publicação seja válida
  Para não quebrar inscrições ativas nem publicar funis incompletos

  Contexto:
    Dado que o serviço de jornadas está disponível
    E que existe uma empresa ativa selecionada

  Cenário: Publicar jornada sem estágio é bloqueado
    Dado um rascunho "Funil Vazio" sem estágios
    Quando "Rafael" tenta publicar a jornada
    Então a publicação é bloqueada
    E a barra de publicação exibe "Adicione ao menos um estágio antes de publicar."

  Cenário: Editar jornada publicada oferece criar nova versão
    Dado uma jornada "Funil de Lançamento" no estado "PUBLICADA"
    Quando "Marina" tenta editar a jornada
    Então o builder permanece somente leitura
    E um banner oferece "criar nova versão"
    Quando "Marina" cria uma nova versão
    Então uma cópia em "RASCUNHO" com versão incrementada é aberta
    E a versão publicada original permanece inalterada

  Cenário: Estágio com ordem duplicada é rejeitado
    Dado um rascunho "Funil de Lançamento" com um estágio na posição 1
    Quando "Marina" adiciona outro estágio na posição 1
    Então o campo de ordem exibe "Já existe um estágio nessa posição."
