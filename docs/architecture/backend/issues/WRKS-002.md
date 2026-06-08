# WRKS-002 -- Modelo de domínio IAM (POJO/records, zero Spring/JPA)

## Contexto
Modelo de domínio puro do IAM: agregados e value objects sem dependência de framework
(RULE-01/02), base para os domain services de RBAC e sessão.

## Spec de referencia
- SPEC-02-identity-session
- SPEC-03-rbac-access-decision
- SPEC-04-data-model-migrations

## Escopo
- `domain/model`: `Usuario`, `Papel`, `Permissao`, `Empresa`, `BusinessUnit`, `Team`,
  `UsuarioEmpresa`, `AccessDecision`, `ModeloAcessoVersao`, `Sessao` (records/POJO).
- Enums `EmpresaStatus {PROVISIONANDO,ATIVA,INATIVA}`, `PapelCanonico {INFOPRODUTOR,HEAD_GROWTH,SDR}`.
- Value objects: `EmpresaId` (regex `^emp_[a-z0-9_]+$`), `PermissaoCodigo`.
- Invariantes embutidas (INV-1..INV-8 do 03-initial-domain-framing).

## Resultado esperado
Domínio compila e testa sem Spring/JPA; invariantes cobertas por testes unitários.

## Criterios de aceite
- [ ] `domain.*` não importa `org.springframework` nem `jakarta.persistence` (ArchUnit RULE-01/02).
- [ ] `EmpresaId` rejeita slug fora do padrão.
- [ ] Testes unitários das invariantes passam.

## Dependencias
- WRKS-001 (precede)

## Estimativa
M

## Prioridade
P1
