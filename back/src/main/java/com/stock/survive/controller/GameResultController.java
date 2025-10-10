package com.stock.survive.controller;

import com.stock.survive.dto.GameResultDto;
import com.stock.survive.dto.tendency.TendencyGameFinishRequest;
import com.stock.survive.dto.tendency.TendencyGameResponse;
import com.stock.survive.service.GameResultService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequiredArgsConstructor
public class GameResultController {
    
    private final GameResultService gameResultService;
    
    @PostMapping("/api/games")
    public ResponseEntity<TendencyGameResponse> finish(Authentication authentication,
                                                       @Valid @RequestBody TendencyGameFinishRequest request) {
        Long userId = (Long) authentication.getPrincipal();
        return ResponseEntity.ok(gameResultService.finish(userId, request));
    }
    
    @GetMapping("/api/games/latest")
    public ResponseEntity<GameResultDto> getLatestResult(Authentication authentication) {
        Long userId = (Long) authentication.getPrincipal();
        GameResultDto latestResult = gameResultService.getLatestByUserNo(userId);
        return ResponseEntity.ok(latestResult);
    }
}