# language: pt
Funcionalidade: Fluxo de aprovação de assets
  Como Infoprodutor (autoridade de publicação)
  Quero aprovar ou rejeitar assets submetidos
  Para garantir que só conteúdo validado seja publicado

  Contexto:
    Dado que o serviço de assets está disponível
    E que existe uma empresa ativa selecionada
    E um usuário "Rafael" com permissões "asst.asset.aprovar" e "asst.asset.publicar"

  Cenário: Fila de aprovação lista assets em revisão
    Dado dois assets no estado "EM_REVISAO"
    Quando "Rafael" abre a tela de aprovações
    Então a fila exibe os dois assets aguardando aprovação

  Cenário: Aprovar um asset submetido
    Dado um asset "Landing de captura" no estado "EM_REVISAO"
    Quando "Rafael" abre o asset na fila e o aprova com comentário "ok, publicar"
    Então o asset passa para o estado "APROVADO"
    E a decisão de aprovação fica registrada com o revisor e o comentário

  Cenário: Rejeição exige comentário
    Dado um asset "Roteiro VSL" no estado "EM_REVISAO"
    Quando "Rafael" tenta rejeitar o asset sem comentário
    Então a rejeição é bloqueada e um comentário é exigido
    Quando ele rejeita com o comentário "ajustar a abertura"
    Então o asset passa para o estado "REJEITADO"
    E o asset retorna para autoria

  Cenário: Ação de publicar indisponível fora de APROVADO
    Dado um asset "Roteiro VSL" no estado "EM_REVISAO"
    Quando "Rafael" abre o asset
    Então a ação de publicar não está disponível
