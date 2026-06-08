# language: pt
Funcionalidade: Base de Conhecimento — curadoria de nós
  Como Marina (Head de Growth) com permissão de escrita
  Quero criar, indexar e arquivar nós de conhecimento
  Para manter a base que alimenta o copiloto curada e atualizada

  Contexto:
    Dado que estou autenticado com permissões "intl.knowledge.read" e "intl.knowledge.write"
    E que a empresa "Acme Cursos" está ativa

  Cenário: Criar e indexar um nó manual
    Dado que estou em "/intl/knowledge"
    Quando clico em "Novo nó"
    E preencho o título "Política de reembolso" e o conteúdo "Reembolso em até 7 dias"
    E adiciono a tag "suporte"
    E salvo o nó
    Então o nó é criado com status "RASCUNHO" e versão 1
    Quando clico em "Indexar"
    E a indexação conclui
    Então o status do nó muda para "INDEXADO"

  Cenário: Indexação indisponível (503) permite tentar de novo
    Dado que tenho um nó "RASCUNHO"
    Quando clico em "Indexar"
    E o serviço de embedding responde 503
    Então o nó permanece em status "RASCUNHO"
    E vejo a mensagem de indisponibilidade temporária
    E a ação "tentar de novo" está disponível

  Cenário: Buscar e arquivar um nó
    Dado que estou em "/intl/knowledge"
    Quando filtro pela tag "suporte"
    Então a lista mostra apenas nós com a tag "suporte"
    Quando arquivo um nó da lista
    Então o status do nó muda para "ARQUIVADO"
    E o nó não é removido permanentemente

  Cenário: Leitor sem permissão de escrita não vê ações de edição
    Dado que estou autenticado apenas com "intl.knowledge.read"
    E que estou em "/intl/knowledge"
    Então não vejo a ação "Novo nó"
    E não vejo as ações de indexar ou arquivar nas linhas
