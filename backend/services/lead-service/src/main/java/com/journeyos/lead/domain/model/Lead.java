package com.journeyos.lead.domain.model;

import java.util.UUID;
import java.time.Instant;

// TODO: complete fields from domain-model-diagram.puml — no Spring/JPA imports (RULE-01, RULE-02)
public record Lead(
    UUID id,
    String tenantId,
    Instant createdAt
    // TODO: add domain fields
) {}
