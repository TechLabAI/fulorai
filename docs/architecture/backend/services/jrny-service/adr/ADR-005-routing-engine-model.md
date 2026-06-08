# ADR-005 — Routing Engine determinístico + decision log imutável + assist de IA com fallback

**Status:** accepted

## Contexto

A dor central de JRNY é a ausência de roteamento explícito e auditável: hoje a decisão de "para
onde vai este lead" é opaca, sem versionamento e sem trilha. Além disso, a recomendação de IA
(`orchestration`) **não pode** ser o único caminho — uma operação não pode parar de rotear leads
porque a IA está fora do ar. Precisamos de um modelo em que a decisão seja determinística e
reproduzível por construção, e a IA seja um aprimoramento opcional sempre auditado.

## Decisão

1. **Motor determinístico primeiro:** o `MotorRoteamento` avalia `regra_roteamento` versionadas
   (condições sobre score/segmento/atributo do lead), ordenadas por `prioridade`. A primeira
   regra satisfeita decide o estágio-alvo. A avaliação é pura (domain service, sem I/O), portanto
   reproduzível: o mesmo `snapshot_entrada` + mesma versão de regras → mesma decisão.

2. **Assist de IA opcional com fallback:** antes (ou junto) da decisão, o motor **pode** consultar
   a TechLab AI (`orchestration`) por uma recomendação de próximo-melhor-estágio. A recomendação:
   - é protegida por timeout + circuit breaker (Resilience4j);
   - em falha/indisponibilidade → a decisão segue **somente** pelas regras (`assist_ia=INDISPONIVEL`);
   - quando usada, é registrada (`assist_ia=USADO`) com a sugestão e a confiança no snapshot;
   - **nunca** sobrepõe uma regra de guarda determinística marcada como obrigatória.

3. **Decision log imutável:** toda decisão grava uma `decisao_roteamento` imutável — `gatilho`,
   `snapshot_entrada`, `regra_id`, `assist_ia`, `resultado` (`ROTEADO`/`SEM_MUDANCA`/`NAO_ROTEADO`),
   `estagio_alvo_id`, `motivo`. Editar uma decisão é proibido; corrigir = nova decisão. O log é
   projetado em Elastic `routing-decisions` (fact).

4. **Jornada versionada, imutável em runtime:** uma `jornada` `PUBLICADA` não é editada in-place;
   alterar = nova `versao`. A `inscricao_jornada` referencia a `jornada_versao` de entrada, então
   inscrições ativas não mudam de definição embaixo do lead.

## Alternativas consideradas

- **Roteamento só por IA (sem regras determinísticas):** flexível, mas não reproduzível, não auditável e frágil a indisponibilidade. Rejeitada (viola o princípio "determinístico primeiro").
- **Decisões mutáveis / sem log:** simples, mas remove a auditabilidade do "por quê" — exatamente a dor que JRNY existe para resolver. Rejeitada.
- **Jornada mutável in-place:** prática para o autor, mas corromperia inscrições ativas (lead muda de funil no meio do caminho). Rejeitada em favor de versionamento.
- **Motor de regras BPMN/engine externo (ex.: Drools/Camunda):** poderoso, mas pesado para o MVP e acopla a um runtime externo; o avaliador determinístico próprio (condições jsonb + prioridade) entrega o necessário com menos complexidade. Adiado.

## Consequências

**Positivas:** decisões reproduzíveis e auditáveis; resiliência total a falha de IA; rollback de jornada trivial (versionamento); proveniência do "por quê" garantida por construção.

**Negativas:** a gramática de `condicao` (predicado jsonb) precisa ser bem especificada e testada; a state machine de inscrição e todas as regras precisam de cobertura BDD (gate D-218); acúmulo de decisões imutáveis (mitigado: payload leve, retenção por tenant).

## Referências

- `03-initial-domain-framing.md` (§4 State Transitions, §5 Invariants)
- `05-persistence-model.md` (`regra_roteamento`, `inscricao_jornada`, `decisao_roteamento`)
- `adr/ADR-003-messaging-strategy.md` (roteamento dirigido por evento; assist resiliente)
- `docs/architecture/integrations/techlab-ai-integration.md` (`orchestration`)
