package com.stock.survive.controller;

import com.stock.survive.service.AuthService;
import com.stock.survive.serviceImpl.GoogleOAuthServiceImpl;
import com.stock.survive.serviceImpl.KakaoOAuthServiceImpl;
import com.stock.survive.serviceImpl.TokenServiceImpl;
import com.stock.survive.serviceImpl.UserLinkServiceImpl;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import lombok.extern.java.Log;
import lombok.extern.log4j.Log4j2;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.security.core.Authentication;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.server.ResponseStatusException;
import org.springframework.web.util.UriComponentsBuilder;

import java.util.Map;

@RestController
@RequiredArgsConstructor
@RequestMapping("/api/users")
@Log4j2
public class AuthController {

    private final KakaoOAuthServiceImpl kakao;
    private final GoogleOAuthServiceImpl google;
    private final UserLinkServiceImpl linker;
    private final TokenServiceImpl tokenServiceImpl;

    //그냥 로그인한 유저 관리하는것도
    private final AuthService authService;

    @Value("${app.front-origin:http://localhost:5173}")
    private String frontOrigin;

    /** 항상 홈(/)로 리다이렉트하는 URL 생성 */
    private String frontHome() {
        // origin 기반으로 path=/ 만 보장
        return UriComponentsBuilder.fromUriString(frontOrigin)
                .replacePath("/")     // 무조건 홈
                .replaceQuery(null)
                .fragment(null)
                .build()
                .toUriString();
    }

    @GetMapping("/login-user")
    public com.stock.survive.dto.UserSummaryDto loginUser(Authentication auth) {
        return authService.me(extractUid(auth));
    }

    // ===== 구글 =====
    @GetMapping("/auth/google")
    public void googleLogin(HttpServletResponse res) throws Exception {
        res.sendRedirect(google.buildAuthorizeUrl());
    }

    @GetMapping("/auth/google/callback")
    public void googleCallback(@RequestParam String code,
                               @RequestParam String state,
                               HttpServletResponse res) {
        try {
            google.verifyState(state);
            var info = google.exchangeAndFetchUser(code);
            var user = linker.linkOrCreateByProvider(info);

            var pair = tokenServiceImpl.issue(user);
            tokenServiceImpl.setRefreshCookie(res, pair.refresh());

            res.sendRedirect(frontHome());
        } catch (Exception e) {
            try { res.sendRedirect(frontOrigin + "/login?error=google_oauth_failed"); } catch (Exception ignored) {}
        }
    }


    // ===== 카카오 =====
    @GetMapping("/auth/kakao")
    public void kakaoLogin(HttpServletResponse res) throws Exception {
        res.sendRedirect(kakao.buildAuthorizeUrl());
    }

    @GetMapping("/auth/kakao/callback")
    public void kakaoCallback(@RequestParam String code,
                              @RequestParam String state,
                              HttpServletResponse res) throws Exception {
        kakao.verifyState(state);
        var info = kakao.exchangeAndFetchUser(code);
        var user = linker.linkOrCreateByProvider(info);

        var pair = tokenServiceImpl.issue(user);
        tokenServiceImpl.setRefreshCookie(res, pair.refresh());

        res.sendRedirect(frontHome());
    }

    /** Access 재발급: Refresh 쿠키 검증/로테이션 후 새 Access 반환 */
    @PostMapping("/auth/refresh")
    public Map<String, String> refresh(HttpServletRequest req, HttpServletResponse res) {
        String newAccess = tokenServiceImpl.refreshFromCookie(req, res);
        return Map.of("accessToken", newAccess);
    }

    /** 로그아웃: Refresh 폐기(서버/쿠키) */
    @PostMapping("/logout")
    public ResponseEntity<Void> logout(HttpServletRequest req, HttpServletResponse res) {
        tokenServiceImpl.revokeFromCookie(req, res);
        return ResponseEntity.noContent().build();
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
