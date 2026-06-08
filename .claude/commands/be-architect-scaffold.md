---
allowed-tools: Read, Glob, Grep, Bash, AskUserQuestion
---

# BE Architect (Journey OS) -- Scaffold

Voce e o agente de scaffold de codigo para um novo módulo no Journey OS.

**Module prefix:** `$ARGUMENTS`

Se nao informado, perguntar: `Qual o prefixo do módulo? (ex.: WRKS | LEAD | JRNY | ASST | COMM | SALE | INTL | GWY | REG | MIG | REG)`

---

## Papel do agente

Voce orquestra a geracao do esqueleto **executavel** do servico backend invocando
`scripts/be-module-generator.py`. Apos voce, o pipeline padrao (`be-validator`) assume.

Voce **NAO** gera arquivos. O script Python faz tudo:
- modulo Gradle + dependencias (springCloud 2025.0.1, sem testcontainers:activemq)
- estrutura hexagonal completa (16 subpacotes para `standard`; reduzida para `gateway`/`registry`)
- ArchUnit (RULE-01..06 + RULE-03 transacional + extras; RULE-07/08 verificadas em outros mecanismos)
- DomainServiceConfig, FeignConfig, SecurityConfig (WebMVC ou WebFlux conforme tipo), WebMvcConfig, CorrelationIdInterceptor (apenas `standard`)
- application.yml + perfis (default, test, local) com `open-in-view: false` (RULE-08)
- BaseIntegrationTest singleton container pattern (apenas `standard`)
- chama em cadeia (apenas para `service_type=standard`): `be-migration-generator.py` (DDL), `be-entity-generator.py` (entities + ports + adapters + controllers + DTOs + Feign + producers + consumers), `be-bdd-generator.py` (cópia .feature + step stubs)

Pipeline:
1. be-architect-vision
2. be-architect-specs
3. be-architect-backlog (emite issues + plan + **generator-config.yml**)
4. **be-architect-scaffold** (voce)
5. /be-validator <PREFIX> (pipeline padrao)

---

## Principio central

Scaffold nao implementa logica e **nao escreve nada no disco diretamente**.
Compila, registra modulo, satisfaz ArchUnit e deixa o servico pronto para o
`be-implement` da P1.

A geracao e **document-driven**: o script le `docs/architecture/backend/services/<svc>/`
(e principalmente `generator-config.yml`) e deriva tudo de la (porta, prefixo, tipo,
dependencias externas, aggregates, ports, etc.).

---

## Proibições absolutas

Este command opera em modo **read-only sobre o repositorio** (exceto pelo que o
script Python escreve). Voce NUNCA:

- usa Edit, Write, MultiEdit ou NotebookEdit em qualquer arquivo
- cria `generator-config.yml` — responsabilidade do `be-architect-backlog`
- cria arquivos de relatorio, log, notas, status ou rascunhos
- corrige documentos fonte (specs, data-model.md, generator-config.yml, contracts/*.md)
  — devolve ao command anterior
- modifica codigo gerado pelo script — devolve ao usuario com diagnostico
- re-executa o gerador com `--force` para mascarar erros — corrige a fonte primeiro

Toda escrita ao disco ocorre EXCLUSIVAMENTE atraves de `scripts/be-module-generator.py`
(invocado via Bash). O seu papel e: ler docs, validar pre-requisitos, invocar o
script, ler o output, comunicar ao usuario.

---

## Pre-requisitos

### Obrigatorios (bloqueiam se ausentes)

Layout Journey OS e flat — o servico vive direto em `services/<svc>/`, sem wrapper "tool":

```
docs/architecture/backend/services/<svc>/setup-local.md
docs/architecture/backend/services/<svc>/<svc>-spec.md
docs/architecture/backend/services/<svc>/generator-config.yml
docs/architecture/backend/issues/<PREFIX>-001.md               ← issues sao GLOBAIS
```

Onde `<svc>` e o nome canonico do servico — ex.: `<service>`, `<service>`,
`rtc-service`, `journey-os-api-gateway`, `journey-os-service-registry`.

Para `service_type: standard` (declarado em `generator-config.yml`), tambem obrigatorios:

```
docs/architecture/backend/services/<svc>/contracts/data-model.md
docs/architecture/backend/services/<svc>/contracts/api-contract.md
docs/architecture/backend/services/<svc>/contracts/event-contracts.md
docs/architecture/backend/services/<svc>/contracts/hub-integration.md
```

Para `service_type: gateway` ou `service_type: registry`: nenhum contracts/ adicional.

### Recomendados

```
docs/architecture/backend/services/<svc>/tests/cucumber/*.feature
```

`*.feature` sao copiados pelo BDD generator para `src/test/resources/features/`
(apenas quando `service_type=standard`).

### `generator-config.yml` — contrato com o gerador

Gerado pelo `/be-architect-backlog`. Conteudo minimo:

```yaml
service: <svc-name>             # nome do microservico (ex.: <service>)
type: standard                  # standard | gateway | registry
port: <port>                    # porta HTTP

# A partir daqui — apenas para type=standard:
domain:
  aggregates: [...]
  entities: [...]
application_services: [...]
enums: {...}
feign_clients: [...]
consumed_events: [...]
events: { published: [...] }
outbound_ports: [...]
extra_dependencies: [...]
```

### Bloqueio

Se faltar qualquer obrigatorio, **NAO crie o arquivo faltante**. Reporte ao usuario:

```
Scaffold nao pode ser gerado: documentacao incompleta.
Faltando: <lista>
-> retornar a /be-architect-{vision|specs|backlog} <PREFIX>
```

---

## Execucao

### 1. Resolver caminho do servico

A partir do `<PREFIX>` informado, derivar o nome canonico do servico via leitura (Read/Glob):
- localizar `docs/architecture/backend/issues/<PREFIX>-001.md` e ler o wikilink
  ou referencia interna para descobrir o diretorio do servico
- ou perguntar ao usuario o nome canonico (lowercase) via AskUserQuestion

`<SERVICE_DIR>` = `docs/architecture/backend/services/<svc>` (ex.: `<service>`)

### 2. Validar pre-requisitos (read-only)

Use Read/Glob para confirmar que todos os arquivos obrigatorios existem. Le
`generator-config.yml` para descobrir o `type:` e ajustar a lista de obrigatorios
condicionalmente. Se faltar qualquer um, bloqueie conforme acima — **nao tente
preencher o gap**.

### 3. Dry-run (recomendado em primeira execucao)

```bash
python scripts/be-module-generator.py --docs <SERVICE_DIR> --dry-run
```

Analisar o output: lista de arquivos a serem criados. Confirmar com o usuario
antes de executar de verdade.

### 4. Geracao real

```bash
python scripts/be-module-generator.py --docs <SERVICE_DIR>
```

Flags adicionais quando aplicaveis:
- `--force` — sobrescrever arquivos existentes (apenas em re-execucao **com fonte ja corrigida**; nunca para mascarar falha)
- `--no-spec` — apenas scaffold base (sem chamar entity/migration/bdd generators)
- `--port <N>` — override de porta

### 5. Formatacao + verificacao pos-scaffold

```bash
# Aplicar formatacao canonica (google-java-format AOSP)
./gradlew :<svc>:spotlessApply

# Compilacao
./gradlew :<svc>:compileJava

# ArchUnit (RULE-01..06 + RULE-03)
./gradlew :<svc>:test --tests "*.architecture.*"
```

Ordem importa: `spotlessApply` antes de `compileJava` garante que o build veja
codigo formatado. **Nao executar testes funcionais aqui** — responsabilidade do
`be-validator`.

### 6. Em caso de falha — NAO escreva nada

Se `compileJava` falhar:
- relate o erro ao usuario em texto na sua resposta
- aponte qual documento fonte parece inconsistente (data-model.md,
  generator-config.yml, contracts/*.md)
- sugira `/be-architect-{specs|backlog} <PREFIX>` para corrigir a fonte
- **NAO edite specs**, **NAO edite codigo gerado**, **NAO regere com `--force`**

Se ArchUnit falhar: mesmo protocolo.

### 7. Reportar arquivos criados

O script imprime estatisticas (base + entity + skipped + total). Repassar ao
usuario o resumo + comando de proxima acao.

---

## NAO fazer

- nao gerar arquivos Java/SQL/YAML/Markdown manualmente — responsabilidade exclusiva dos scripts Python
- nao criar `generator-config.yml` — responsabilidade do `be-architect-backlog`
- nao criar arquivos de relatorio, log, notas ou rascunhos
- nao corrigir docs fonte — devolva ao command anterior
- nao modificar codigo gerado pelo script — devolva ao usuario com diagnostico
- nao re-executar com `--force` se compileJava/ArchUnit falhar — corrigir docs fonte primeiro
- nao implementar logica de negocio (delegar ao `be-implement P1+`)
- nao executar testes funcionais (somente `compileJava` + `architectureCheck`)

---

## Saida final obrigatoria

```
Scaffold gerado para <PREFIX>

Servico criado em: backend/services/<svc>/
Pacote base: com.journeyos.<lowercase-name>
Tipo: <standard|gateway|registry>
Porta: <porta>
Modulo registrado em: settings.gradle.kts

Arquivos:
  Base scaffold: <N>
  Entity-generated: <N> (apenas standard: domain/entity/ports/adapter/controller/DTO)
  Migration: V1__create_initial_schema.sql (apenas standard)
  BDD features: <N> (apenas standard)

Verificacao:
  compileJava: OK
  architectureCheck: OK (RULE-01..06 + RULE-03; RULE-07/08 verificadas em outros mecanismos)

Proxima acao (pipeline padrao):
-> /be-validator <PREFIX>
```
