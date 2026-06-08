package com.journeyos.asst.api.controller;

import com.journeyos.asst.application.port.in.VersaoAssetUseCase;
import com.journeyos.asst.shared.audit.AuditAction;
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
@RequestMapping("/asst-service/versao-asset")
@RequiredArgsConstructor
public class VersaoAssetController {

    private final VersaoAssetUseCase versaoAssetUseCase;

}
