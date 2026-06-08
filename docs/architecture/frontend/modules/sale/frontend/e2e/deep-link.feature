# language: pt
Funcionalidade: Deep links e flags do SALE
  Como usuário com permissão
  Quero acessar telas do SALE por deep link e respeitar feature flags
  Para entrar direto no contexto certo e controlar features por tenant

  Contexto:
    Dado que o serviço de vendas está disponível
    E que existe uma empresa ativa selecionada
    E que "Lucas" tem permissão "sale.oportunidade.read" e "sale.ltv.read"

  Cenário: Acesso à raiz redireciona para o pipeline
    Quando "Lucas" navega para "/sale"
    Então o sistema redireciona para "/sale/pipeline"

  Cenário: Deep link direto ao detalhe da oportunidade
    Dado uma oportunidade "Plano Pro - Acme" existente
    Quando "Lucas" navega direto para "/sale/opportunities/{id}"
    Então o detalhe da oportunidade "Plano Pro - Acme" é exibido

  Cenário: Deep link para oportunidade inexistente
    Quando "Lucas" navega para "/sale/opportunities/inexistente"
    Então o sistema exibe o estado "oportunidade não encontrada"

  Cenário: Flag revenue-dashboard desabilitada oculta a rota e o menu
    Dado que a flag "sale.revenue-dashboard" está desabilitada
    Então o deep link "Receita" não aparece no menu
    E a rota "/sale/dashboard" não está disponível

  Cenário: Flag revenue-dashboard habilitada expõe o dashboard
    Dado que a flag "sale.revenue-dashboard" está habilitada
    Quando "Lucas" navega para "/sale/dashboard"
    Então o dashboard de receita é exibido
