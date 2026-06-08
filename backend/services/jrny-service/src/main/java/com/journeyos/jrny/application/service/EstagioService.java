package com.journeyos.jrny.application.service;

import com.journeyos.jrny.application.port.in.EstagioUseCase;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Slf4j
@Service
@RequiredArgsConstructor
@Transactional
public class EstagioService implements EstagioUseCase {

}
