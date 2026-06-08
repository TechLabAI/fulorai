# language: pt
Funcionalidade: Resolução de canal por regra de roteamento
  Como Head de Growth
  Quero definir regras que escolhem o canal preferido e o fallback
  Para que cada lead receba a mensagem no melhor canal disponível

  Contexto:
    Dado que o serviço de comunicação está disponível
    E que existe uma empresa ativa selecionada
    E um usuário "Marina" com permissões "comm.roteamento.criar", "comm.roteamento.ler" e "comm.mensagem.enviar"

  Cenário: Regra prefere WhatsApp e cai para e-mail como fallback
    Dado uma regra com canal preferido "WHATSAPP" e fallback "EMAIL" para o segmento "quente"
    Quando um disparo é roteado para um lead do segmento "quente" sem WhatsApp
    Então o canal resolvido é "EMAIL"
    E a decisão de roteamento é auditável na UI

  Cenário: Nenhum canal resolvível orienta o usuário
    Dado um disparo sem canal informado e sem regra aplicável
    Quando "Marina" tenta disparar
    Então um aviso de "nenhum canal resolvido" é exibido
    E é oferecida a opção de escolher um canal manualmente ou criar uma regra

  Cenário: Regras são listadas por prioridade
    Dado múltiplas regras com prioridades diferentes
    Quando "Marina" abre a tela de roteamento
    Então as regras são exibidas ordenadas por prioridade
