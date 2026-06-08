# language: pt
Funcionalidade: Copilot — respostas degradadas e não-fundamentadas
  Como usuário do copiloto
  Quero que a UI sinalize claramente quando a resposta não é fundamentada ou está degradada
  Para nunca confundir uma resposta incerta com um fato confirmado

  Contexto:
    Dado que estou autenticado com permissão "intl.copilot.use"
    E que a empresa "Acme Cursos" está ativa
    E que estou numa conversa em "/intl/copilot/c-001"

  Cenário: Resposta NAO_FUNDAMENTADA não exibe citações
    Quando envio uma pergunta sem evidência suficiente na base
    E a resposta é recebida com status "NAO_FUNDAMENTADA"
    Então a bolha exibe o badge "Sem evidência suficiente"
    E não exibe nenhum chip de citação
    E exibe um texto auxiliar explicando que não há base para responder com confiança

  Cenário: Resposta DEGRADADA quando a IA está indisponível
    Dado que a IA (TechLab AI) está indisponível
    Quando envio a pergunta "Qual copy converteu melhor?"
    E a resposta é recebida com status "DEGRADADA"
    Então a bolha exibe o badge "Modo recuperação"
    E o serviço não retorna erro 5xx
    E a resposta nunca é apresentada como fato confirmado

  Cenário: Falha de transporte vira bolha de erro com retry
    Quando envio uma pergunta e ocorre uma falha de rede
    Então a bolha do copiloto exibe o estado "Falha"
    E minha pergunta original permanece preservada no thread
    E vejo a ação "tentar de novo"
