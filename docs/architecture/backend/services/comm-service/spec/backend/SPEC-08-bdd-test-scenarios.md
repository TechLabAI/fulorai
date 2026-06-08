# SPEC-08 — BDD Test Scenarios

> EARS guide linkado. Catálogo de cenários + steps reutilizáveis. Features Gherkin puro em `tests/cucumber/*.feature`.

## Objetivo

Mapear as cláusulas SHALL das specs para cenários BDD (gate D-218) e documentar os step
definitions reutilizáveis usados pelas três features.

## Features

| Feature | Arquivo | Cobre |
|---|---|---|
| Message dispatch & delivery lifecycle | `tests/cucumber/message-dispatch.feature` | SPEC-02, SPEC-05, SPEC-09 |
| Template authoring, composition & rendering | `tests/cucumber/template-rendering.feature` | SPEC-01, SPEC-02, SPEC-10 |
| Channel routing & provider-agnostic dispatch | `tests/cucumber/channel-routing.feature` | SPEC-03, SPEC-06, SPEC-10 |

## Steps reutilizáveis (glue)

- **Given** `an active empresa "<slug>" with provisioned schema` — fixa `EmpresaContextHolder` no tenant de teste.
- **Given** `an authenticated user "<u>" with permissions "<csv>"` — monta JWT/AccessDecision stub.
- **Given** `an ATIVO template "<nome>" for channel "<canal>" with body "<corpo>"` — seed de template.
- **Given** `an active channel config "<canal>" with provider "<provedor>"` — seed de `config_canal` + adapter stub.
- **When** `marina dispatches template "<t>" to lead "<l>" with variables ...` — `POST /messages`.
- **When** `the dispatch worker sends it and the provider accepts/rejects it` — aciona o worker com adapter stub.
- **When** `a valid provider webhook reports "<tipo>" for "<provedorMessageId>"` — `POST /webhooks/{canal}`.
- **Then** `the message delivery state is "<estado>"` / `a "<evento>" event is emitted` / `the error code is "<code>"`.

## Dados de exemplo

- Empresa `emp_acme`; leads `lead-1` (com WhatsApp+email), `lead-2` (só email).
- Provedores stub: `META_WABA`, `SES`, `TELEGRAM_BOT`, `TWILIO` (envio + callback determinísticos).
- TechLab AI stub: modos `available` / `unavailable` para o Template Studio.

## Critérios de aceite (EARS)

- `THE SYSTEM SHALL have at least one BDD scenario for every SHALL clause across SPEC-01..SPEC-10 (gate D-218).`
- `THE SYSTEM SHALL run the Cucumber suite under Testcontainers (PostgreSQL) with provider/TechLab AI adapters stubbed.`
- `THE SYSTEM SHALL keep all .feature files as pure Gherkin (no .md) so be-bdd-generator.py picks them up.`
