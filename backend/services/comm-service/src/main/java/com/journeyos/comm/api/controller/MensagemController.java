package com.journeyos.comm.api.controller;

import com.journeyos.comm.application.port.in.MensagemUseCase;
import com.journeyos.comm.shared.audit.AuditAction;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

// Security: @PreAuthorize derived from rbac.arch.json via the module generator.
// To change which permission gates a method, edit rbac.arch.json and re-run
// be-module-generator.py; do not patch the annotation by hand.
@Slf4j
@RestController
@RequestMapping("/comm-service/mensagem")
@RequiredArgsConstructor
public class MensagemController {

    private final MensagemUseCase mensagemUseCase;

}
