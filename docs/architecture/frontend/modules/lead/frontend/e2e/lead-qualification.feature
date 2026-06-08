# language: pt
Funcionalidade: Qualificação de leads (fila priorizada → detalhe → breakdown 6D → requalificar)
  Como operação de growth/SDR do Journey OS
  Quero ver a fila priorizada e entender o Maturity Score de cada lead
  Para priorizar quem abordar com base num score explicável

  Contexto:
    Dado que o serviço de leads está disponível
    E que existe uma empresa ativa selecionada

  Cenário: Golden path — fila priorizada, breakdown 6D e requalificação
    Dado um usuário "Lucas" com permissão "lead.lead.read"
    Quando ele abre a fila de leads
    Então a fila é exibida ordenada por Maturity Score em ordem decrescente
    Quando ele filtra pelo segmento "Quentes"
    Então apenas leads do segmento "Quentes" são listados
    Quando ele seleciona o lead "Ana Souza"
    Então o detalhe do lead exibe as 6 dimensões do Maturity Score
    E o detalhe exibe a versão de regra que produziu o score
    E o detalhe exibe o selo de assist de IA
    Quando ele clica em "Requalificar" com permissão "lead.qualification.executar"
    Então o Maturity Score é recalculado e o breakdown é atualizado

  Cenário: Score sempre acompanhado do breakdown
    Dado um lead "Bruno Lima" com Maturity Score calculado
    Quando "Lucas" abre o detalhe do lead
    Então o número agregado nunca é exibido sem as 6 dimensões
    E a faixa do score é exibida com rótulo textual além da cor
