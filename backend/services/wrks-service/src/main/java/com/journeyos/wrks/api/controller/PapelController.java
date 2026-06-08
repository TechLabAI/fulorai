package com.journeyos.wrks.api.controller;

import com.journeyos.wrks.application.port.in.PapelUseCase;
import com.journeyos.wrks.shared.audit.AuditAction;
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
@RequestMapping("/wrks-service/papel")
@RequiredArgsConstructor
public class PapelController {

    private final PapelUseCase papelUseCase;

}
