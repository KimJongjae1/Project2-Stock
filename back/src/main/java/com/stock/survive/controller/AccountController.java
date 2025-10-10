package com.stock.survive.controller;

import com.stock.survive.dto.UserStockHoldingDto;
import com.stock.survive.service.AccountService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.security.Principal;

@RestController
@RequestMapping("/api/trade")
@RequiredArgsConstructor
public class AccountController {

    private final AccountService accountService;

    @GetMapping("/holding/{ticker}")
    public ResponseEntity<UserStockHoldingDto> getUserStockHolding(
            Principal principal,
            @PathVariable String ticker) {
        Long userNo = Long.parseLong(principal.getName());
        UserStockHoldingDto holding = accountService.getUserStockHolding(userNo, ticker);

        return ResponseEntity.ok(holding);
    }
}
