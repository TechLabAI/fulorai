# language: pt
Funcionalidade: Copilot — resposta fundamentada
  Como Rafael (Infoprodutor) com a empresa ativa selecionada
  Quero perguntar ao copiloto e receber uma resposta com citações verificáveis
  Para confiar na resposta e checar a evidência que a sustenta

  Contexto:
    Dado que estou autenticado com permissão "intl.copilot.use"
    E que a empresa "Acme Cursos" está ativa
    E que estou na rota "/intl/copilot"

  Cenário: Pergunta retorna resposta RESPONDIDA com citações
    Quando abro uma nova conversa
    E envio a pergunta "Por que o funil caiu esta semana?"
    Então vejo imediatamente minha pergunta no thread
    E vejo a bolha do copiloto em estado "pensando" com a opção de cancelar
    Quando a resposta é recebida com status "RESPONDIDA"
    Então a bolha exibe o badge "Fundamentada"
    E exibe ao menos um chip de citação
    Quando clico no primeiro chip de citação
    Então o painel de citação mostra o trecho e o índice do documento-fonte

  Cenário: Não posso enviar uma segunda pergunta enquanto a anterior está pendente
    Quando envio a pergunta "Resuma o contexto do lead 8821"
    E a bolha do copiloto está em estado "pensando"
    Então o botão de enviar está desabilitado
    E o campo de pergunta não aceita novo envio até a resposta chegar

  Cenário: Cancelar uma pergunta em andamento
    Quando envio a pergunta "Gere um relatório completo"
    E a resposta ainda está "pensando"
    E clico em "Cancelar"
    Então a bolha pendente do copiloto desaparece
    E o texto da pergunta volta para o campo de entrada
