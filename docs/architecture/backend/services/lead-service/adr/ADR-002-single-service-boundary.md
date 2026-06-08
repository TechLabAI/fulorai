# ADR-002 — Single-Service Boundary (sem decomposição no MVP)

**Status:** accepted

## Contexto

LEAD reúne capture, perfil, surveys, qualification rules, Maturity Score e segmentação.
Poderia ser tentador separar, por exemplo, um "scoring engine" como serviço próprio. É preciso
decidir a granularidade no MVP.

## Decisão

Manter LEAD como **um único serviço** (`lead-service`). Todas as capacidades compartilham o
agregado raiz **Lead** e operam dentro do mesmo ciclo transacional curto no schema `emp_<slug>`.
A separação interna é feita por **pacotes/portas** (hexagonal), não por processos.

## Alternativas consideradas

- **Scoring como microserviço dedicado**: introduz chamada de rede e consistência distribuída no
  caminho crítico (capturar→qualificar), sem ganho de escala comprovado no MVP. Rejeitada (mantida
  como evolução futura se o volume de recálculo exigir).
- **Surveys como serviço separado**: surveys existem para alimentar o perfil do lead; separar criaria
  acoplamento chato sem dono claro do dado. Rejeitada.

## Consequências

**Positivas:** transação local simples no `emp_<slug>`; menos latência no golden path; menos
superfície operacional; evolução para fora do limite só quando houver evidência de necessidade.

**Negativas:** o serviço cresce em responsabilidades; mitigado por fronteiras de pacote rígidas
(ArchUnit) e portas explícitas, que permitem extrair um adapter/serviço depois sem reescrever o domínio.

## Referências

- `04-backend-architecture-direction.md` (§2 Service Boundary)
- ADR-001 (hexagonal)
