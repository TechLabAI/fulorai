# BE Architect (Journey OS) -- Specs Validate

Voce e o agente que **executa** as EARS specs como teste BDD. Roda
`be-spec-to-bdd.py` para gerar `.feature` Gherkin + step stubs Java a
partir das specs do módulo, e valida que o build do servico compila.

**Module prefix:** `$ARGUMENTS`

Se nao informado, perguntar: `Qual o prefixo do módulo a validar? (ex.: WRKS | LEAD | JRNY | ASST | COMM | SALE | INTL | GWY | REG | MIG)`

---

## Papel do agente

Specs EARS sao escritas em `/be-architect-specs`. Drift em prod e detectado em
`/be-architect-drift-check`. Falta o elo do meio: garantir que **toda nova
SHALL clause vira um cenario BDD que falha enquanto nao for implementado**.

Esse comando fecha o Gap 1 (Pole Position v3 — S10):

- Gera `.feature` Gherkin a partir das EARS clauses do modulo.
- Gera `{Module}StepDefs.java` com `PendingException` em cada step (D-214).
- Gera `CucumberSpringContext.java` + `application-bdd.properties` (D-215).
- Roda `./gradlew :services:<servico>:compileTestJava` para validar
  que os stubs compilam.
- Reporta cenarios `passing` / `pending` / `failing`.

Pipeline:
1. /be-architect-vision
2. /be-architect-specs
3. **/be-architect-specs-validate (voce — Gap 1, D-218)**
4. /be-architect-backlog
5. /be-architect-scaffold

---

## Pre-requisitos

1. Specs EARS existem em `docs/architecture/backend/services/<module>-service/spec/`.
2. Servico ja tem `build.gradle.kts`. Se nao, peca para rodar
   `/be-architect-scaffold` primeiro -- mas note que o ciclo recomendado e
   gerar specs antes de scaffold (D-218).
3. Cucumber deps presentes em `build.gradle.kts`. Se faltar, rodar:
   ```
   python scripts/be-spec-to-bdd.py emit-build-patch
   ```
   e colar o output dentro do bloco `dependencies { ... }` do servico.

---

## Passos

### 1. Resolver paths

Do prefixo do modulo (`$ARGUMENTS`), resolver:

- `MODULE_PREFIX` = `$ARGUMENTS` (uppercase, ex.: `OBR`)
- `SERVICE_NAME` = servico mapeado em `project-context.json` (`modules[].backendService`)
- `SPEC_DIR` = `docs/architecture/backend/services/<SERVICE_NAME>/spec/`
- `SERVICE_DIR` = `backend/services/<SERVICE_NAME>/`
- `PACKAGE` = `com.journeyos.<module-lower>`

### 2. Rodar o gerador

```bash
python scripts/be-spec-to-bdd.py generate \
    --module $MODULE_PREFIX \
    --spec-root $SPEC_DIR \
    --output-root $SERVICE_DIR \
    --package $PACKAGE \
    --emit-spring-context
```

Output esperado:
```
OK: be-spec-to-bdd generate <MODULE>
     N EARS clause(s) -> N scenario(s)
     wrote src/test/resources/features/<module>.feature
     wrote src/test/java/<pkg>/bdd/<Module>StepDefs.java
     wrote src/test/java/<pkg>/bdd/CucumberSpringContext.java
     wrote src/test/resources/application-bdd.properties
```

### 3. Compilar (gate 1 -- estrutural)

```bash
./gradlew :services:$SERVICE_NAME:compileTestJava
```

Se falhar:
- Falta Cucumber no `build.gradle.kts` -> rodar
  `python scripts/be-spec-to-bdd.py emit-build-patch` e colar o output.
- Falta `spring-security-test` (necessario para `jwt()` request post-processor)
  -> adicionar `testImplementation("org.springframework.security:spring-security-test")`.

### 4. Rodar os cenarios (gate 2 -- comportamental)

```bash
./gradlew :services:$SERVICE_NAME:test --tests "*CucumberIT*"
```

Resultado esperado **na primeira execucao**:
- 0 scenarios `passed`
- N scenarios `pending` (todos os recem-gerados)
- 0 scenarios `failed`

Esse e o estado correto. Os testes ficam **pending** ate o time
implementar cada step. Pending nao quebra o build do CI por default --
para fazer pendings falharem (apos uma janela de carencia), configurar
`-Dcucumber.execution.strict=true`.

### 5. Diff review

Listar os arquivos gerados:

```bash
git status backend/services/$SERVICE_NAME/src/test/
```

Esperado:
- `src/test/resources/features/<module>.feature` (novo)
- `src/test/java/.../bdd/<Module>StepDefs.java` (novo)
- `src/test/java/.../bdd/CucumberSpringContext.java` (novo, idempotente)
- `src/test/resources/application-bdd.properties` (novo, idempotente)

Apresentar ao usuario:

```markdown
## Specs validate -- <MODULE>

- EARS clauses processadas: N
- Cenarios gerados: N
- Distribuicao por padrao EARS:
  - event: X
  - unwanted: Y
  - ubiquitous: Z
  - optional: W
  - state: K
- Compilacao test classpath: PASS / FAIL
- Cenarios pending: N (esperado na primeira execucao)
- Step defs gerados: <ClassName>.java
```

### 6. Confirmar commit

Perguntar ao usuario:
> "Os arquivos gerados estao corretos? Posso commitar como
> `feat($MODULE): Cucumber BDD harness from EARS specs`?"

Se sim, commitar somente os 4 arquivos acima. Step defs **nao devem ser
editados** entre o `generate` e o commit -- senao a regeneracao perde
trabalho. Implementacao dos steps vem em commits subsequentes.

---

## Convencoes

- **Re-gerar e seguro:** rodar `be-spec-to-bdd generate` de novo sobrescreve
  o `.feature` (estado verdadeiro = spec). Step defs sao sobrescritos
  **somente para steps com mesma assinatura**; metodos com texto diferente
  causam orfaos (lint manual).
- **Versionamento:** `.feature` e step defs sao commitados. PR review olha
  o diff do `.feature` como contrato; o do step defs como esqueleto.
- **Estado pending no CI:** ate o time decidir, pendings sao tratados como
  warning (verde). Habilitar strict mode em servicos maduros.

---

## Erros comuns

| Erro | Causa | Remediar |
|---|---|---|
| `no EARS clauses found` | Specs vazias ou padrao nao reconhecido | Verificar que cada SHALL clause segue um dos 5 padroes EARS (D-057). |
| `compileTestJava` falha em `PendingException` | Versao errada de Cucumber | Rodar `emit-build-patch` e alinhar a versao. |
| `compileTestJava` falha em `jwt()` | Falta `spring-security-test` | Adicionar dep de teste. |
| Step orfao apos regeneracao | Texto do step mudou na spec | Remover o metodo antigo manualmente; relogar o spec. |

---

## Referencias

- `scripts/be-spec-to-bdd.py` -- gerador (S10).
- `scripts/be-bdd-generator.py` -- gerador legado de step defs a partir
  de `.feature` ja escritos (D-NNN anterior). Os dois sao complementares:
  S10 cobre o caso "spec -> .feature"; o legado cobre "feature -> stubs".
- `templates/operational/code/gradle/build-cucumber-bdd-patch.gradle.kts.j2`
  -- patch standalone para servicos sem o bdd_block.
- Decisoes: D-214 (PendingException), D-215 (stack 7.18.0),
  D-216 (heuristica EARS->Gherkin), D-218 (posicao no pipeline).
