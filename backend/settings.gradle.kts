// Root settings.gradle.kts for journey-os
// TODO[lote-6a]: render from templates/operational/infra/backend-settings.gradle.kts.j2

rootProject.name = "journey-os-backend"

// Service modules expected (from project-context.modules.registry).
// Uncomment each line after /be-architect-scaffold scaffolds the service:
include(":services:wrks-service")
include(":services:lead-service")
include(":services:jrny-service")
include(":services:asst-service")
include(":services:comm-service")
include(":services:sale-service")
include(":services:intl-service")
// include(":services:gwy-service")
include(":services:journey-os-service-registry")
include(":services:journey-os-migrations")
include(":services:journey-os-api-gateway")
