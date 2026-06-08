# language: pt
Funcionalidade: Modelos de atribuição — criar e ativar versão
  Como Head de Growth
  Quero ativar uma versão de modelo de atribuição
  Para re-atribuir a receita de forma governável e explicável

  Contexto:
    Dado que o serviço de vendas está disponível
    E que existe uma empresa ativa selecionada
    E que "Marina" tem permissão "sale.atribuicao.read", "sale.atribuicao.criar" e "sale.atribuicao.ativar"

  Cenário: Fallback LAST_TOUCH enquanto nenhuma versão está ativa
    Dado que nenhum modelo de atribuição está ativo
    Quando "Marina" navega para "/sale/attribution"
    Então o modelo efetivo exibido é "LAST_TOUCH"

  Cenário: Criar uma versão de modelo nasce inativa
    Dado que "Marina" está na tela de atribuição
    Quando ela cria uma versão de modelo do tipo "FIRST_TOUCH"
    Então a nova versão aparece como inativa

  Cenário: Ativar uma versão re-atribui as compras afetadas
    Dado uma versão de modelo "FIRST_TOUCH" inativa
    Quando "Marina" ativa essa versão
    Então a versão passa a ativa e a anterior é desativada
    E as compras afetadas são re-atribuídas

  Cenário: Ativar versão inexistente
    Quando "Marina" tenta ativar uma versão que não existe
    Então o sistema rejeita com "404 sale.atribuicao.modelo-nao-encontrado"
    E uma mensagem inline é exibida na linha do modelo

  Cenário: Ativar versão com soma inválida
    Dado uma versão de modelo cujo cálculo não fecha com a receita
    Quando "Marina" tenta ativar essa versão
    Então o sistema rejeita com "409 sale.atribuicao.soma-invalida"
    E um banner de erro é exibido
    E a versão não é marcada como ativa
