# language: pt
Funcionalidade: Analítica — leitura consolidada (read-only)
  Como Rafael (Infoprodutor)
  Quero ver o funil consolidado e o uso/custo do copiloto
  Para acompanhar o negócio sem montar relatório manual

  Contexto:
    Dado que estou autenticado com permissão "intl.analytics.read"
    E que a empresa "Acme Cursos" está ativa
    E que estou na rota "/intl/analytics"

  Cenário: Carregar funil e uso do copiloto
    Quando a página de analítica carrega
    Então vejo o gráfico de funil com suas etapas e totais
    E vejo o painel de uso do copiloto com total de respostas, custo de tokens e taxas

  Cenário: Filtrar por período
    Quando seleciono o período "últimos 7 dias"
    Então o funil é recarregado para o período selecionado
    E o painel de uso reflete o mesmo escopo de empresa

  Cenário: Analítica é somente leitura
    Quando inspeciono as telas de analítica
    Então não existe nenhuma ação de escrita ou edição disponível
