package com.journeyos.wrks.application.service;

import com.journeyos.wrks.application.port.in.AuditoriaUseCase;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Slf4j
@Service
@RequiredArgsConstructor
@Transactional
public class AuditoriaService implements AuditoriaUseCase {

}
