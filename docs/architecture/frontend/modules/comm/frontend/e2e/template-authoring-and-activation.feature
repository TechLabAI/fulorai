# language: pt
Funcionalidade: Autoria e ativação de template
  Como Head de Growth
  Quero criar e editar templates com placeholders e controlá-los por estado
  Para padronizar a comunicação com versões aprovadas

  Contexto:
    Dado que o serviço de comunicação está disponível
    E que existe uma empresa ativa selecionada
    E um usuário "Marina" com permissões "comm.template.criar", "comm.template.editar" e "comm.template.publicar"

  Cenário: Criar e ativar um template de WhatsApp
    Quando "Marina" cria um template "Boas-vindas" no canal "WHATSAPP" do tipo "TRANSACIONAL"
    Então o template é criado no estado "RASCUNHO"
    Quando "Marina" edita o corpo para "Olá {{nome}}!" e declara a variável "nome"
    E salva o template
    E ativa o template
    Então o template passa para o estado "ATIVO"

  Cenário: Placeholder não declarado bloqueia o salvamento
    Dado um template "Oferta" no estado "RASCUNHO"
    Quando "Marina" edita o corpo para "Olá {{nome}}, veja {{produto}}" e declara apenas "nome"
    Então o editor sinaliza a variável "produto" como não declarada
    E o salvamento é bloqueado até a correção

  Cenário: E-mail exige assunto
    Quando "Marina" cria um template no canal "EMAIL" sem assunto
    Então a validação exige o preenchimento do assunto
    E o template não é salvo

  Cenário: Arquivar um template não apaga mensagens já enviadas
    Dado um template "Antigo" no estado "ATIVO" referenciado por mensagens enviadas
    Quando "Marina" arquiva o template
    Então o template passa para o estado "ARQUIVADO"
    E as mensagens já enviadas continuam consultáveis
