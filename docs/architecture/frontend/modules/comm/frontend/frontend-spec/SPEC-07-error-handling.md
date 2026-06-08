# SPEC-07 — Error Handling — COMM · Frontend

> `ProblemDetail` (BE, RFC 7807) → `AppError` (`@journeyos/shared/error-model`) → mensagem
> user-facing (`@journeyos/shared/ui-feedback`). Códigos espelham `comm-service/api-contract.md` §5.

## Mapeamento `failure_code` → UI

| HTTP · code | Mensagem (pt-BR) | Apresentação | Retry |
|---|---|---|---|
| `422 comm.template.canal-invalido` | "Canal inválido." | inline (campo) | corrigir |
| `422 comm.template.tipo-invalido` | "Tipo de template inválido." | inline (campo) | corrigir |
| `422 comm.template.nome-obrigatorio` | "Informe um nome para o template." | inline (campo) | corrigir |
| `422 comm.template.assunto-obrigatorio` | "E-mail exige um assunto." | inline (campo, só EMAIL) | corrigir |
| `422 comm.template.variavel-nao-declarada` | "Há variáveis no corpo não declaradas: {lista}." | inline (editor) | corrigir |
| `404 comm.template.nao-encontrado` | "Template não encontrado." | banner + voltar ao catálogo | — |
| `409 comm.template.nao-ativo` | "Só é possível disparar com um template ATIVO." | banner no disparo + CTA "Ativar" | corrigir |
| `404 comm.mensagem.nao-encontrada` | "Mensagem não encontrada." | banner + voltar à lista | — |
| `422 comm.mensagem.variavel-ausente` | "Preencha a variável obrigatória: {nome}." | inline (form disparo) | corrigir |
| `409 comm.mensagem.estado-invalido` | "Transição de entrega inválida." | toast (raro) | — |
| `422 comm.roteamento.sem-canal` | "Nenhum canal pôde ser resolvido. Escolha um canal ou crie uma regra." | banner + CTA roteamento | corrigir |
| `422 comm.canal.nao-configurado` | "Canal sem configuração ativa." | banner + CTA `/comm/channels` | corrigir |
| `409 comm.canal.duplicado` | "Já existe configuração para este canal e provedor." | inline (form canal) | corrigir |
| `503 comm.studio.ia-indisponivel` | "IA indisponível no momento. Você pode editar manualmente." | banner no Studio (degradado) | botão "Tentar de novo" + CTA manual |
| `503 comm.canal.provedor-indisponivel` | "Provedor do canal indisponível — a mensagem ficou como FALHADA." | na timeline | (BE reprocessa) |
| `401 comm.auth.token-invalido` | (delegado à Access Layer) | re-login | — |
| `403 comm.acesso.permissao-negada` | "Você não tem permissão para esta ação." | estado "sem permissão" | — |

## Critérios de aceite (EARS)

- **C-07.1 (Ubiquitous):** `THE SYSTEM SHALL converter todo ProblemDetail do comm-service em AppError via error-model antes de exibir`
- **C-07.2 (Unwanted):** `IF o disparo é rejeitado com comm.template.nao-ativo, THEN THE SYSTEM SHALL bloquear o envio e oferecer a ação de ativar o template sem criar mensagem`
- **C-07.3 (Unwanted):** `IF o Template Studio retorna comm.studio.ia-indisponivel, THEN THE SYSTEM SHALL exibir o estado degradado e manter o corpo do template inalterado e oferecer edição manual`
- **C-07.4 (Unwanted):** `IF o roteamento não resolve canal com comm.roteamento.sem-canal, THEN THE SYSTEM SHALL orientar o usuário a escolher canal manual ou criar uma regra`
- **C-07.5 (Unwanted):** `IF uma config de canal duplicada é submetida com comm.canal.duplicado, THEN THE SYSTEM SHALL exibir erro inline no formulário sem criar duplicata`
- **C-07.6 (Event-driven):** `WHEN o provedor falha com comm.canal.provedor-indisponivel levando ao estado FALHADA, THE SYSTEM SHALL refletir a falha na timeline com o motivoFalha`
- **C-07.7 (Ubiquitous):** `THE SYSTEM SHALL usar mensagens inline para validação de formulário e banner para erros de contexto recuperáveis e toast para erros transitórios não bloqueantes`

## Referências

- BE: `comm-service/contracts/api-contract.md` §5 · `shared/contratos/error-model.md`
- `05-state-and-data-flow.md` §5 · ADR-005 (falha de provedor na timeline)
