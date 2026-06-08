# JRNY-015 -- Observability + health (Actuator, métricas, MDC, logs estruturados)

## Contexto
Instrumentação operacional do JRNY: health liveness/readiness, métricas de roteamento (latência de
avaliação, taxa de fallback do assist de IA) e logs estruturados com correlação.

## Spec de referencia
- SPEC-07-observability-health

## Escopo
- Actuator: liveness/readiness; readiness `UP` mesmo com TechLab AI/Elastic degradados (são opcionais/best-effort).
- Métricas (Micrometer): contagem de decisões por `resultado`, latência da avaliação de regras,
  latência/erro da chamada TechLab AI, **taxa de `assist_ia=INDISPONIVEL`** (fallback determinístico).
- Logs estruturados (`@Slf4j`, nunca `System.out`) com `correlationId`/`empresaId`/`leadId` via MDC.

## Resultado esperado
Operação observável: dá para medir saúde do roteamento e quanto a IA está degradada sem afetar o serviço.

## Criterios de aceite
- [ ] `/actuator/health` expõe liveness e readiness.
- [ ] Métrica de taxa de fallback do assist de IA disponível.
- [ ] Logs carregam `correlationId`/`empresaId` (e `leadId` no roteamento).
- [ ] Readiness não cai por TechLab AI/Elastic indisponíveis.

## Dependencias
- JRNY-001 (bootstrap)

## Estimativa
S

## Prioridade
P7
