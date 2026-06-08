# language: pt
Funcionalidade: Configuração segura de canais
  Como Infoprodutor
  Quero configurar provedores de canal por empresa sem expor segredos
  Para enviar mensagens com identidade própria mantendo as credenciais seguras

  Contexto:
    Dado que o serviço de comunicação está disponível
    E que existe uma empresa ativa selecionada
    E um usuário "Rafael" com permissões "comm.canal.configurar" e "comm.canal.ler"

  Cenário: Configurar um canal guarda apenas a referência de credencial
    Quando "Rafael" configura o canal "WHATSAPP" com o provedor "META_WABA" e a identidade "+5511999999999"
    E informa a referência de credencial "secret://comm/whatsapp"
    Então a configuração é criada
    E a referência de credencial é exibida mascarada
    E o segredo em claro nunca é exibido nem retornado

  Cenário: Configuração duplicada é rejeitada
    Dado uma configuração existente para o canal "WHATSAPP" e provedor "META_WABA"
    Quando "Rafael" tenta criar outra configuração para o mesmo canal e provedor
    Então um erro de configuração duplicada é exibido no formulário
    E nenhuma configuração duplicada é criada
