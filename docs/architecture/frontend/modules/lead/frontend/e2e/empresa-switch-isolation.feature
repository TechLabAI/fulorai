# language: pt
Funcionalidade: Isolamento por empresa na fila de leads
  Como operação multi-empresa do Journey OS
  Quero que a troca de empresa invalide a fila em tela
  Para nunca vazar leads de uma empresa para outra (LGPD)

  Contexto:
    Dado que o serviço de leads está disponível
    E um usuário com acesso às empresas "A" e "B"

  Cenário: Troca de empresa invalida a fila anterior
    Dado que a empresa "A" está ativa
    E a fila exibe leads da empresa "A"
    Quando o usuário troca para a empresa "B"
    Então a fila da empresa "A" é invalidada antes de renderizar
    E nenhum lead da empresa "A" aparece sob a empresa "B"
