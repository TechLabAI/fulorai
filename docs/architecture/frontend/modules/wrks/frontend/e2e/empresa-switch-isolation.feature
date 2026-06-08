# language: pt
Funcionalidade: Troca de empresa sem vazamento cross-empresa
  Como usuário que opera múltiplas empresas
  Quero trocar de empresa sem recarregar
  Para que nenhum dado de uma empresa apareça no contexto de outra

  Cenário: Trocar de empresa recarrega o escopo e não vaza dados
    Dado um usuário autenticado operando a empresa "A"
    E a lista de usuários da empresa "A" carregada na tela
    Quando ele troca para a empresa "B" pela topbar
    Então o contexto ativo passa a ser a empresa "B"
    E nenhum usuário da empresa "A" permanece visível
    E a lista de usuários é recarregada no escopo da empresa "B"
    E nenhuma requisição pendente da empresa "A" atualiza a tela

  Cenário: Requisição em voo é cancelada na troca
    Dado um usuário autenticado operando a empresa "A"
    E uma requisição de lista da empresa "A" ainda em andamento
    Quando ele troca para a empresa "B"
    Então a requisição da empresa "A" é cancelada
    E somente dados da empresa "B" são exibidos
