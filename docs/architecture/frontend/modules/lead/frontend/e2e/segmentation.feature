# language: pt
Funcionalidade: Segmentação dinâmica de leads
  Como Head de Growth do Journey OS
  Quero criar segmentos por predicado sobre perfil e score
  Para reagrupar a base e navegar à fila de cada segmento

  Contexto:
    Dado que o serviço de leads está disponível
    E que existe uma empresa ativa selecionada
    E um usuário "Marina" com permissões "lead.segment.read" e "lead.segment.criar"

  Cenário: Criar segmento com prévia de contagem e navegar à fila
    Quando "Marina" cria um segmento "Quentes" com um predicado válido
    Então uma prévia da contagem de leads do predicado é exibida
    Quando ela salva o segmento
    Então o segmento "Quentes" aparece na lista de segmentos
    Quando ela abre o segmento "Quentes"
    Então a fila de leads filtrada pelo segmento é exibida

  Cenário: Predicado inválido é rejeitado com erro de campo
    Quando "Marina" informa um predicado inválido
    Então um erro de campo no predicado é exibido
    E o editor de segmento permanece aberto
