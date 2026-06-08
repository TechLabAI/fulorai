# JRNY-009 -- Assist de IA (TechLab AI orchestration) opcional com fallback determinístico

## Contexto
O `MotorRoteamento` pode consultar a TechLab AI (`orchestration`) por uma recomendação de
próximo-melhor-estágio. O assist é **opcional**: protegido por timeout + circuit breaker e, em
falha, a decisão segue só pelas regras (`assist_ia=INDISPONIVEL`). Nunca caminho crítico.

## Spec de referencia
- SPEC-02-routing-engine-orchestration
- SPEC-10-integrations
- techlab-ai-integration.md

## Escopo
- Adapter `RecomendacaoIaPort` → cliente HTTP TechLab AI (`orchestration`); DTOs gerados de
  `integrations/techlab-ai/openapi.json` (não hand-written), em `gen/techlabai/`.
- Resilience4j: timeout curto + circuit breaker + retry limitado; `fallback` retorna "sem recomendação".
- Registro do estado do assist na decisão: `USADO` (recomendação aplicada), `IGNORADO`
  (recomendação descartada por regra de guarda), `INDISPONIVEL` (falha/timeout).
- Regra de guarda determinística obrigatória nunca é sobreposta pelo assist.

## Resultado esperado
Com TechLab AI disponível, a recomendação enriquece a decisão; indisponível, o roteamento
determinístico decide sozinho — sem bloqueio.

## Criterios de aceite
- [ ] IA disponível → decisão pode registrar `assist_ia=USADO` com a recomendação no snapshot.
- [ ] IA indisponível/timeout → `assist_ia=INDISPONIVEL` e decisão pelas regras (sem erro ao chamador).
- [ ] Circuit breaker abre após o limiar e não derruba o roteamento.
- [ ] Nenhuma chamada a provider de IA direto (somente via TechLab AI HTTP).

## Dependencias
- JRNY-004 (precede)
- INT-JRNY-003 (contrato/DTOs TechLab AI)

## Estimativa
M

## Prioridade
P4
