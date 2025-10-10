package com.stock.survive.controller;

import com.stock.survive.dto.MyPageDto;
import com.stock.survive.service.MyPageService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;

import java.util.Set;

@RestController
@RequiredArgsConstructor
@RequestMapping("/api/mypage")
public class MyPageController {

    private final MyPageService myPageService;

    @GetMapping("/me")
    public MyPageDto me(Authentication auth) {
        return myPageService.getMyPage(extractUid(auth));
    }

    // 메인/리스트 별표(★) 표시에 최적
    @GetMapping("/me/favorite-ids")
    public Set<Long> favoriteIds(Authentication auth) {
        return myPageService.getFavoriteIdSet(extractUid(auth));
    }

    private Long extractUid(Authentication auth) {
        if (auth == null || !auth.isAuthenticated())
            throw new ResponseStatusException(HttpStatus.UNAUTHORIZED, "UNAUTHORIZED");
        Object p = auth.getPrincipal();
        if (p instanceof Long i) return i;
        if (p instanceof Number n) return (long) n.intValue();
        try { return Long.valueOf(Integer.valueOf(String.valueOf(p))); } catch (Exception ignored) {}
        throw new ResponseStatusException(HttpStatus.UNAUTHORIZED, "INVALID_PRINCIPAL");
    }
}