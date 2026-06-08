package com.journeyos.jrny.infrastructure.clients;

import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.web.bind.annotation.*;

@FeignClient(name = "", url = "${}")
public interface AssetQueryClient {

    // TODO: add methods from techlab-ai-integration.md
}
