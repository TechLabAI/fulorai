package com.journeyos.asst.application.service;

import com.journeyos.asst.application.port.in.BuscaAssetUseCase;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Slf4j
@Service
@RequiredArgsConstructor
@Transactional
public class BuscaAssetService implements BuscaAssetUseCase {

}
