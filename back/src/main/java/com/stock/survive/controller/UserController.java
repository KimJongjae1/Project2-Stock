package com.stock.survive.controller;

import com.stock.survive.dto.UserSummaryDto;
import com.stock.survive.service.UserService;
import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;

@RestController
@RequiredArgsConstructor
@RequestMapping("/api/users")
public class UserController {

    private final UserService userService;

    public record NickReq(@NotBlank String nickname) {}

    /** 닉네임 변경 */
    @PatchMapping("/me")
    @Transactional
    public UserSummaryDto updateNickname(Authentication auth, @Valid @RequestBody NickReq req) {
        return userService.changeNickname(extractUid(auth), req.nickname());
    }

    /** 회원 탈퇴 */
    @DeleteMapping("/me")
    @Transactional
    public ResponseEntity<Void> deleteMe(Authentication auth) {
        userService.deleteMe(extractUid(auth));
        return ResponseEntity.noContent().build();
    }

    private Long extractUid(Authentication auth) {
        if (auth == null || !auth.isAuthenticated())
            throw new ResponseStatusException(HttpStatus.UNAUTHORIZED, "UNAUTHORIZED");
        Object p = auth.getPrincipal();
        if (p instanceof Long i) return i;
        if (p instanceof Number n) return (long) n.intValue();
        try { return Long.valueOf(String.valueOf(p)); } catch (Exception ignored) {}
        throw new ResponseStatusException(HttpStatus.UNAUTHORIZED, "INVALID_PRINCIPAL");
    }
}