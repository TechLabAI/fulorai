# ASST-009 -- Asset Studio: composição via TechLab AI (document_composition)

## Contexto
Composição/edição de conteúdo assistida por IA, delegada ao TechLab AI, produzindo nova versão
imutável em RASCUNHO com proveniência.

## Spec de referencia
- SPEC-03-asset-studio-composition
- contracts/techlab-ai-integration.md

## Escopo
- `ComposicaoIaPort` (out) + `ComporNoStudioService` (application).
- `AssetStudioController`: `POST /{id}/studio/compose`.
- Cria `versao_asset` (origem=ASSET_STUDIO, RASCUNHO) com `brief_composicao` gravado.
- Nunca publica automaticamente. Resiliência/fallback em INT-ASST-003.

## Resultado esperado
Brief → rascunho composto pela IA, com proveniência; degradação graciosa se IA indisponível.

## Criterios de aceite
- [ ] Sucesso → 201 versão origem=ASSET_STUDIO em RASCUNHO + `brief_composicao` persistido.
- [ ] IA indisponível/timeout → 503 `asst.studio.ia-indisponivel`, nenhuma versão criada.
- [ ] Studio nunca publica versão automaticamente.

## Dependencias
- ASST-004 (versão); INT-ASST-003 (cliente TechLab AI)

## Estimativa
L

## Prioridade
P4
