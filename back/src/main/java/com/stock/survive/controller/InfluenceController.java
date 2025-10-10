package com.stock.survive.controller;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;

@Slf4j
@RestController
@RequiredArgsConstructor
@RequestMapping("/api/influence")
public class InfluenceController {

    private final WebClient webClient;

    // 외부 JSON을 그대로 프록시하여 반환
    @GetMapping(produces = MediaType.APPLICATION_JSON_VALUE)
    public Mono<ResponseEntity<String>> proxyInfluence(
            @RequestParam("path") String path,
            @RequestParam(value = "top", required = false) Integer top
    ) {
        String baseUrl = "http://j13a301a.p.ssafy.io:8888/influence";

        WebClient.UriSpec<?> uriSpec = webClient.get();
        WebClient.RequestHeadersSpec<?> req = uriSpec.uri(builder -> builder
                .scheme("http")
                .host("j13a301a.p.ssafy.io")
                .port(8888)
                .path("/influence")
                .queryParam("path", path)
                .queryParamIfPresent("top", top == null ? java.util.Optional.empty() : java.util.Optional.of(top))
                .build());
        log.info(req.toString());
        return req.retrieve()
                .toEntity(String.class);
    }
}


