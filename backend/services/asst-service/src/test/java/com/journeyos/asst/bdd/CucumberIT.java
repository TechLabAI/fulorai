package com.journeyos.asst.bdd;

import io.cucumber.junit.platform.engine.Constants;
import org.junit.platform.suite.api.*;

/**
 * Cucumber integration test runner — asst-service.
 *
 * Runs all .feature files in src/test/resources/features/.
 * Requires a running Spring context (Testcontainers via BaseIntegrationTest).
 */
@Suite
@IncludeEngines("cucumber")
@SelectClasspathResource("features")
@ConfigurationParameter(
    key = Constants.GLUE_PROPERTY_NAME,
    value = "com.journeyos.asst.bdd"
)
@ConfigurationParameter(
    key = Constants.PLUGIN_PROPERTY_NAME,
    value = "pretty, html:build/reports/cucumber/cucumber-report.html"
)
public class CucumberIT {}
