# language: pt
Funcionalidade: Disparo e rastreio do ciclo de vida da mensagem
  Como SDR
  Quero disparar uma mensagem para um lead e acompanhar o status de entrega
  Para saber se a mensagem foi enviada, entregue e lida

  Contexto:
    Dado que o serviço de comunicação está disponível
    E que existe uma empresa ativa selecionada
    E um usuário "Lucas" com permissões "comm.mensagem.enviar" e "comm.mensagem.ler"
    E um template "Boas-vindas" no canal "WHATSAPP" no estado "ATIVO"
    E um canal "WHATSAPP" com configuração ativa

  Cenário: Golden path — disparo aceito e rastreado até a leitura
    Quando "Lucas" dispara o template "Boas-vindas" para o lead "Rafael" com a variável "nome"="Rafael"
    Então a mensagem é aceita com o estado de entrega "ENFILEIRADA"
    E a mensagem aparece no histórico
    Quando "Lucas" abre o detalhe da mensagem
    Então o rastreio é iniciado por polling
    E a linha do tempo avança para "ENVIADA"
    E a linha do tempo avança para "ENTREGUE"
    E a linha do tempo avança para "LIDA"
    E o rastreio por polling é encerrado ao atingir o estado terminal

  Cenário: Disparo sobre template não-ativo é bloqueado
    Dado um template "Rascunho de oferta" no estado "RASCUNHO"
    Quando "Lucas" tenta disparar o template "Rascunho de oferta"
    Então o disparo é bloqueado com a mensagem de template não ATIVO
    E é oferecida a ação de ativar o template
    E nenhuma mensagem é criada

  Cenário: Falha de provedor reflete na linha do tempo
    Quando "Lucas" dispara o template "Boas-vindas" para o lead "Rafael"
    E o provedor do canal está indisponível
    Então a mensagem evolui para o estado "FALHADA"
    E a linha do tempo exibe o motivo da falha
