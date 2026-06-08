package com.journeyos.comm.application.service;

import com.journeyos.comm.application.port.in.MensagemUseCase;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Slf4j
@Service
@RequiredArgsConstructor
@Transactional
public class MensagemService implements MensagemUseCase {

}
