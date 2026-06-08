# language: pt
Funcionalidade: Administração de usuários
  Como Infoprodutor (CEO da operação)
  Quero convidar usuários e atribuir papéis
  Para montar minha equipe com os acessos corretos

  Contexto:
    Dado um usuário autenticado com papel "INFOPRODUTOR"
    E a empresa "Operação Rafael" como contexto ativo
    E que ele está na tela "/wrks/users"

  Cenário: Convidar um novo usuário como SDR
    Quando ele aciona "Convidar"
    E preenche o e-mail "lucas@empresa.com" com papel "SDR"
    E confirma o convite
    Então o usuário "lucas@empresa.com" aparece na tabela com status "convidado"

  Cenário: E-mail duplicado é rejeitado
    Quando ele convida um e-mail que já pertence a um usuário ativo
    Então uma mensagem de erro no campo e-mail informa que o usuário já existe
    E nenhum novo usuário é criado

  Cenário: Anti-escalonamento de papel
    Dado um usuário autenticado com papel "HEAD_GROWTH"
    Quando ele tenta atribuir o papel "INFOPRODUTOR" a outro usuário
    Então a operação é rejeitada com erro de escalonamento
    E o papel do outro usuário permanece inalterado
