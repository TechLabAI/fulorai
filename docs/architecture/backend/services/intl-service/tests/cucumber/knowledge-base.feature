Feature: Base de Conhecimento — curadoria e indexação

# Refs: SPEC-03 (knowledge base), api-contract §2, event-contracts §2
# Invariantes: INV-1 (rastreabilidade), INV-4 (idempotência)

Background:
  Given uma empresa "acme" provisionada com base de conhecimento
  And um usuário autenticado com a permissão "intl.knowledge.write"

Scenario: Criar nó manual inicia em RASCUNHO
  When o usuário cria um nó de conhecimento manual com título e conteúdo
  Then o nó é criado com status "RASCUNHO" e versão 1
  And a fonte do nó tem tipo "MANUAL"

Scenario: Indexar nó projeta no índice knowledge-nodes
  Given um nó de conhecimento em "RASCUNHO"
  And a TechLab AI está disponível para gerar embedding
  When o usuário indexa o nó
  Then o nó passa para status "INDEXADO"
  And um documento é projetado no índice "knowledge-nodes" com o bloco de rastreabilidade

Scenario: Falha de embedding mantém o nó em RASCUNHO
  Given um nó de conhecimento em "RASCUNHO"
  And a TechLab AI está indisponível para gerar embedding
  When o usuário tenta indexar o nó
  Then o serviço responde 503
  And o nó permanece em status "RASCUNHO"
  And nenhum documento parcial é projetado

Scenario: Editar nó indexado incrementa versão e reindexa
  Given um nó de conhecimento "INDEXADO" na versão 1
  When o usuário edita o conteúdo do nó
  Then a versão do nó passa para 2
  And o documento em "knowledge-nodes" é reprojetado

Scenario: Ingestão por asset.versao.publicada cria nó fonte ASSET
  When o evento "journey-os.asset.versao.publicada" é consumido para "asset-123:2"
  Then existe um nó de conhecimento com fonte tipo "ASSET" e referência "asset-123:2"

Scenario: Reentrega do mesmo asset atualiza o nó em vez de duplicar
  Given já existe um nó de conhecimento para "asset-123:2"
  When o evento "journey-os.asset.versao.publicada" para "asset-123:2" é reentregue
  Then continua existindo exatamente um nó para "asset-123:2"

Scenario: Arquivar nó não faz hard-delete
  Given um nó de conhecimento "INDEXADO"
  When o usuário arquiva o nó
  Then o nó tem status "ARQUIVADO"
  And o nó ainda é recuperável para auditoria
