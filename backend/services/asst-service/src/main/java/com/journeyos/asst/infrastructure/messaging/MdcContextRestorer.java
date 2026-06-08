package com.journeyos.asst.infrastructure.messaging;

import com.journeyos.asst.infrastructure.security.TenantContextHolder;
import jakarta.jms.JMSException;
import jakarta.jms.Message;
import org.slf4j.MDC;

/**
 * Restores MDC (correlationId) and TenantContextHolder (tenantId) on the consumer
 * thread from JMS message headers. Async listeners MUST call restore() at start
 * and clear() in finally — RULE-07 (CLAUDE.md).
 */
public final class MdcContextRestorer {

    public static final String CORRELATION_PROPERTY = "correlationId";
    public static final String TENANT_PROPERTY = "tenantId";
    public static final String MDC_CORRELATION_KEY = "correlationId";

    private MdcContextRestorer() {}

    public static void restore(Message message) throws JMSException {
        String correlationId = message.getStringProperty(CORRELATION_PROPERTY);
        if (correlationId != null && !correlationId.isBlank()) {
            MDC.put(MDC_CORRELATION_KEY, correlationId);
        }
        String tenantId = message.getStringProperty(TENANT_PROPERTY);
        if (tenantId != null && !tenantId.isBlank()) {
            TenantContextHolder.set(tenantId);
        }
    }

    public static void clear() {
        MDC.remove(MDC_CORRELATION_KEY);
        TenantContextHolder.clear();
    }
}
