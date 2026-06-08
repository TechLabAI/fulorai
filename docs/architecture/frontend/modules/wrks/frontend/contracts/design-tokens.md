# Design Tokens — WRKS

> WRKS **não** introduz tokens próprios no MVP: consome integralmente
> `@journeyos/shared/ui-tokens`. Este documento existe para registrar a decisão e listar os tokens
> compartilhados que as telas de admin do WRKS mais utilizam.

## Decisão

- **Zero tokens locais** no MVP. Telas de login, seleção de empresa, dashboard e administração usam
  apenas os tokens e componentes de `@journeyos/shared/{ui-tokens, ui-components, ui-feedback}`.
- Qualquer token específico do WRKS (improvável) entraria em `libs/wrks/styles` e seria promovido a
  `shared` se reutilizado (regra "se repete, promova", blueprint-core).

## Tokens compartilhados mais usados (referência)

| Categoria | Uso no WRKS |
|---|---|
| Cores de superfície / texto | Cards de empresa, tabela de usuários, formulários |
| Espaçamento / grid | Layout de dashboard e settings |
| Estados (success/warn/error) | Status de usuário (`ativo`/`inativo`/`convidado`), feedback de erro |
| Tipografia | Títulos de página / breadcrumbs |

> A fonte canônica dos valores é `frontend/libs/shared/ui-tokens` (a migrar dos tokens de design do
> projeto). WRKS não duplica valores.
