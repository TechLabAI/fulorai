package com.journeyos.intl.application.service;

import com.journeyos.intl.application.port.in.AnalyticsUseCase;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Slf4j
@Service
@RequiredArgsConstructor
@Transactional
public class AnalyticsService implements AnalyticsUseCase {

}
