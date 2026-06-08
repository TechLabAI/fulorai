# ADR-004 — Multi-tenancy: resolução e propagação de `empresa`

- **Status:** accepted

## Contexto

O Journey OS é multi-tenant com isolamento **schema-per-empresa** (`journeyos_global` /
`t_<empresaId>`), termo de negócio `empresa`. Os serviços de domínio precisam saber **qual
empresa** atende cada requisição para escolher o schema. Decidir o papel do gateway nesse fluxo.

## Decisão

O gateway **resolve** o tenant a partir do JWT validado e o **propaga** via headers, sem nunca
acessar o banco:

- Extrai `empresaId` do claim do JWT (após ADR-003).
- Injeta `X-Empresa-Id` e (se aplicável) `X-Tenant-Schema` nos headers da requisição downstream.
- **Anti-spoofing (INV-3):** esses headers são derivados **somente** do claim; quaisquer
  `X-Empresa-Id`/`X-Tenant-Schema` enviados pelo cliente são **descartados** na borda.
- O gateway **não** abre conexão com PostgreSQL nem resolve schema; quem aplica
  `schema-per-empresa` é cada serviço de negócio (via `EmpresaContextHolder`).

## Alternativas consideradas

1. **Tenant resolvido por subdomínio/host:** acopla roteamento a DNS por tenant; menos flexível
   que claim no token; rejeitado como mecanismo primário.
2. **Cada serviço extrai o tenant do próprio JWT:** válido como defesa em profundidade, mas
   propagar via header padroniza o contrato e simplifica os serviços. Combinado (header primário;
   serviços podem revalidar).
3. **Gateway resolve o schema no banco:** violaria o princípio stateless e criaria acoplamento ao
   PostgreSQL. Rejeitado.

## Consequências

**Positivas:** contrato de tenant uniforme e à prova de spoofing; serviços recebem o `empresaId`
pronto; gateway permanece stateless e sem banco. **Negativas:** confiança no header propagado
(mitigada por revalidação opcional nos serviços e por stripping de headers de entrada).

## Referências

- `docs/architecture/shared/multi-empresa.md` (estratégia schema-per-empresa)
- ADR-003 (origem dos claims)
