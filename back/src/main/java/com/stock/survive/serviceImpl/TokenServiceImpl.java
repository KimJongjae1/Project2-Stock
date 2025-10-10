package com.stock.survive.serviceImpl;

import com.stock.survive.entity.User;
import com.stock.survive.repository.UserRepository;
import com.stock.survive.security.refresh.RefreshTokenStore;
import com.stock.survive.service.TokenService;
import com.stock.survive.util.JWTUtil;
import jakarta.servlet.http.Cookie;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseCookie;
import org.springframework.stereotype.Service;
import org.springframework.web.server.ResponseStatusException;

import java.time.Duration;
import java.util.Map;

import static org.springframework.http.HttpStatus.UNAUTHORIZED;

@Service
@RequiredArgsConstructor
public class TokenServiceImpl implements TokenService {

    private final JWTUtil jwtUtil;
    private final RefreshTokenStore refreshStore;
    private final UserRepository userRepository;

    @Value("${jwt.access-exp-minutes:60}") private long accessExpMin;
    @Value("${jwt.refresh-exp-days:14}")  private long refreshExpDays;

    @Value("${app.cookie.secure:true}")    private boolean cookieSecure;
    @Value("${app.cookie.same-site:None}") private String cookieSameSite;
    @Value("${app.cookie.domain:}")        private String cookieDomain;

    private static final String REFRESH_COOKIE = "refresh_token";

    public record Pair(String access, String refresh) {}

    /** 최초 발급 */
    public Pair issue(User u) {
        String access = generateAccess(u);
        String refresh = refreshStore.issue(u.getId(), Duration.ofDays(refreshExpDays));
        return new Pair(access, refresh);
    }

    private String generateAccess(User u) {
        return jwtUtil.generateToken(
                Map.of("uid", u.getId(),
                        "email", u.getSocialEmail(),
                        "nickname", u.getNickname()),
                Duration.ofMinutes(accessExpMin));
    }

    /** ---- Refresh 쿠키 제어 ---- */
    public void setRefreshCookie(HttpServletResponse res, String refresh) {
        ResponseCookie.ResponseCookieBuilder b = ResponseCookie.from(REFRESH_COOKIE, refresh)
                .httpOnly(true)
                .secure(cookieSecure)
                .sameSite(cookieSameSite)
                .path("/")
                .maxAge(Duration.ofDays(refreshExpDays));
        if (cookieDomain != null && !cookieDomain.isBlank()) {
            b.domain(cookieDomain);
        }
        res.addHeader("Set-Cookie", b.build().toString());
    }

    public void clearRefreshCookie(HttpServletResponse res) {
        ResponseCookie.ResponseCookieBuilder b = ResponseCookie.from(REFRESH_COOKIE, "")
                .httpOnly(true)
                .secure(cookieSecure)
                .sameSite(cookieSameSite)
                .path("/")
                .maxAge(Duration.ZERO);
        if (cookieDomain != null && !cookieDomain.isBlank()) {
            b.domain(cookieDomain);
        }
        res.addHeader("Set-Cookie", b.build().toString());
    }

    /** 요청에서 refresh 쿠키 읽기 */
    public String readRefreshCookie(HttpServletRequest req) {
        Cookie[] cookies = req.getCookies();
        if (cookies == null) return null;
        for (Cookie c : cookies) if (REFRESH_COOKIE.equals(c.getName())) return c.getValue();
        return null;
    }

    /** refresh 검증 → 로테이션 → 새 access 반환 */
    public String refreshFromCookie(HttpServletRequest req, HttpServletResponse res) {
        String raw = readRefreshCookie(req);
        if (raw == null) throw new ResponseStatusException(UNAUTHORIZED, "NO_REFRESH_COOKIE");

        Long userNo = refreshStore.verify(raw);
        if (userNo == null) throw new ResponseStatusException(UNAUTHORIZED, "INVALID_REFRESH");

        // 로테이션
        refreshStore.revoke(raw);
        String newRaw = refreshStore.issue(userNo, Duration.ofDays(refreshExpDays));
        setRefreshCookie(res, newRaw);

        // Access 재발급 (닉/이메일을 클레임에 실으니 조회)
        User user = userRepository.findById(userNo)
                .orElseThrow(() -> new ResponseStatusException(UNAUTHORIZED, "USER_NOT_FOUND"));
        return generateAccess(user);
    }

    /** refresh 폐기 + 쿠키 삭제 */
    public void revokeFromCookie(HttpServletRequest req, HttpServletResponse res) {
        String raw = readRefreshCookie(req);
        if (raw != null) refreshStore.revoke(raw);
        clearRefreshCookie(res);
    }
}
