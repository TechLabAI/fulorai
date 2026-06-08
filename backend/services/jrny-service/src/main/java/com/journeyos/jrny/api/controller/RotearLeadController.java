package com.journeyos.jrny.api.controller;

import com.journeyos.jrny.application.port.in.RotearLeadUseCase;
import com.journeyos.jrny.shared.audit.AuditAction;
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
@RequestMapping("/jrny-service/rotear-lead")
@RequiredArgsConstructor
public class RotearLeadController {

    private final RotearLeadUseCase rotearLeadUseCase;

}
