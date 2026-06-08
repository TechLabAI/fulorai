# language: pt
Funcionalidade: Regras de roteamento versionadas
  Como Head de Growth
  Quero versionar regras que decidem o estágio-alvo de cada lead
  Para tornar o roteamento governável e auditável

  Contexto:
    Dado que o serviço de jornadas está disponível
    E que existe uma empresa ativa selecionada
    E que "Marina" tem permissão "jrny.regra.criar" e "jrny.regra.editar"
    E uma jornada "Funil de Lançamento" com estágios "Nutrição" e "Oferta"

  Cenário: Criar uma regra de roteamento válida
    Quando "Marina" cria uma regra de "Nutrição" para "Oferta"
    E define a condição "scoreAgregado >= 70 E dimensoes.INTENCAO >= 80"
    E define a prioridade 100
    Então a regra é criada com versão 1 e ativa
    E aparece na lista ordenada por prioridade

  Cenário: Editar uma regra incrementa a versão
    Dado uma regra ativa versão 1 na jornada
    Quando "Marina" altera a condição da regra
    Então a regra passa a versão 2
    E as decisões anteriores continuam referenciando a versão 1

  Cenário: Condição com campo fora da gramática é rejeitada
    Quando "Marina" cria uma regra com a condição referenciando "campoInexistente"
    Então o construtor de condição exibe "Condição inválida: revise os campos/operadores."

  Cenário: Estágio-destino fora da jornada é rejeitado
    Quando "Marina" cria uma regra cujo destino não pertence à jornada
    Então o seletor de destino exibe "O estágio-destino não pertence a esta jornada."
