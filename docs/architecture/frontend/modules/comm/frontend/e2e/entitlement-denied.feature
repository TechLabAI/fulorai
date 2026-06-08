# language: pt
Funcionalidade: Negação de acesso por permissão
  Como sistema
  Quero ocultar e bloquear ações sem a permissão correspondente
  Para respeitar o RBAC do workspace

  Contexto:
    Dado que o serviço de comunicação está disponível
    E que existe uma empresa ativa selecionada

  Cenário: Usuário sem permissão de envio não vê o disparo
    Dado um usuário "Visitante" sem a permissão "comm.mensagem.enviar"
    Quando "Visitante" abre a tela de mensagens
    Então a ação de disparar mensagem não é exibida

  Cenário: Rota sem permissão é bloqueada
    Dado um usuário "Visitante" sem a permissão "comm.roteamento.ler"
    Quando "Visitante" tenta acessar a tela de roteamento
    Então o acesso é bloqueado com o estado "sem permissão"
    E nenhuma chamada de roteamento é feita ao backend

  Cenário: Deep link de menu some sem a permissão
    Dado um usuário "Visitante" sem a permissão "comm.canal.ler"
    Quando o menu de comunicação é montado
    Então o item "Canais" não é exibido
