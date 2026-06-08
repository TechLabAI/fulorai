# language: pt
Funcionalidade: Isolamento por empresa na troca de contexto
  Como usuário multi-empresa
  Quero que a troca de empresa nunca mostre dados de outra empresa
  Para garantir isolamento e conformidade (LGPD)

  Contexto:
    Dado que o serviço de comunicação está disponível
    E um usuário "Marina" com acesso às empresas "Alpha" e "Beta"

  Cenário: Trocar de empresa limpa o catálogo em tela
    Dado que "Marina" está na empresa "Alpha" com o catálogo de templates carregado
    Quando "Marina" troca para a empresa "Beta"
    Então o catálogo da empresa "Alpha" é invalidado antes do recarregamento
    E apenas templates da empresa "Beta" são exibidos

  Cenário: Trocar de empresa encerra o rastreio em andamento
    Dado que "Marina" está acompanhando a linha do tempo de uma mensagem da empresa "Alpha"
    Quando "Marina" troca para a empresa "Beta"
    Então o rastreio por polling da mensagem da empresa "Alpha" é encerrado
    E nenhuma mensagem da empresa "Alpha" permanece em tela
