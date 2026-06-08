# language: pt
Funcionalidade: Idempotência de disparo
  Como SDR
  Quero que cliques duplos ou reprocessos não dupliquem mensagens
  Para nunca enviar a mesma mensagem duas vezes ao lead

  Contexto:
    Dado que o serviço de comunicação está disponível
    E que existe uma empresa ativa selecionada
    E um usuário "Lucas" com permissão "comm.mensagem.enviar"
    E um template "Boas-vindas" no estado "ATIVO"
    E um canal "WHATSAPP" com configuração ativa

  Cenário: Duplo clique no botão enviar produz um único envio
    Quando "Lucas" clica em "Enviar" duas vezes seguidas para o lead "Rafael"
    Então uma única mensagem é criada
    E ambas as requisições usam a mesma chave de idempotência
    E o botão de enviar fica desabilitado enquanto a requisição está em andamento

  Cenário: Replay da mesma chave de idempotência não cria nova mensagem
    Dado que uma mensagem já foi disparada com uma chave de idempotência conhecida
    Quando a mesma requisição de disparo é reenviada com a mesma chave
    Então a UI reflete a mensagem existente
    E nenhuma nova mensagem é criada
