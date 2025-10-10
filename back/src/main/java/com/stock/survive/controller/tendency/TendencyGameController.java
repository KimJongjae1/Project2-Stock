package com.stock.survive.controller.tendency;

import com.stock.survive.dto.tendency.TendencyGameOrderRequest;
import com.stock.survive.dto.tendency.TendencyGameStartRequest;
import com.stock.survive.dto.tendency.TendencyGameStateResponse;
import com.stock.survive.service.TendencyGameService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequiredArgsConstructor
@RequestMapping("/api/games/tendency")
public class TendencyGameController {

    private final TendencyGameService tendencyGameService;

    @PostMapping
    public ResponseEntity<TendencyGameStateResponse> start(Authentication authentication,
                                                           @Valid @RequestBody(required = false) TendencyGameStartRequest request) {
        Long userId = (Long) authentication.getPrincipal();
        TendencyGameStateResponse response = tendencyGameService.start(userId, request);
        return ResponseEntity.status(HttpStatus.CREATED).body(response);
    }

    @GetMapping("/{sessionId}")
    public ResponseEntity<TendencyGameStateResponse> state(Authentication authentication,
                                                           @PathVariable Long sessionId) {
        Long userId = (Long) authentication.getPrincipal();
        return ResponseEntity.ok(tendencyGameService.getState(userId, sessionId));
    }

    @PostMapping("/{sessionId}/orders")
    public ResponseEntity<TendencyGameStateResponse> order(Authentication authentication,
                                                           @PathVariable Long sessionId,
                                                           @Valid @RequestBody TendencyGameOrderRequest request) {
        Long userId = (Long) authentication.getPrincipal();
        return ResponseEntity.ok(tendencyGameService.placeOrder(userId, sessionId, request));
    }

    @PostMapping("/{sessionId}/next-week")
    public ResponseEntity<TendencyGameStateResponse> nextWeek(Authentication authentication,
                                                              @PathVariable Long sessionId) {
        Long userId = (Long) authentication.getPrincipal();
        return ResponseEntity.ok(tendencyGameService.proceedNextWeek(userId, sessionId));
    }

}
