package com.stock.survive.security.filter;

import com.stock.survive.util.JWTUtil;
import io.jsonwebtoken.Claims;
import io.jsonwebtoken.ExpiredJwtException;
import io.jsonwebtoken.JwtException;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import lombok.extern.log4j.Log4j2;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.web.authentication.WebAuthenticationDetailsSource;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.List;
import java.util.Map;
@Component
@RequiredArgsConstructor
@Log4j2
public class JWTCheckFilter extends OncePerRequestFilter {

    private final JWTUtil jwtUtil;

    private static final List<String> WHITELIST_PREFIXES = List.of(
        "/oauth2/**",
        "/login/oauth2/**",
        "/users/auth/**",
        "/api/users/auth/**",
        "/error",
        "/actuator/health","/actuator/info",
        "/favicon.ico"
    );
    

    private boolean isWhitelisted(HttpServletRequest req) {
        String path = req.getRequestURI();
        for (String p : WHITELIST_PREFIXES) {
            if (path.startsWith(p)) return true;
        }
        return false;
    }

    @Override
    protected boolean shouldNotFilter(HttpServletRequest request) {
        boolean shouldSkip = isWhitelisted(request);
        return shouldSkip;
    }

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response,
                                    FilterChain chain) throws ServletException, IOException {

        String path = request.getRequestURI();
        String method = request.getMethod();
        String header = request.getHeader(HttpHeaders.AUTHORIZATION);


        if (header == null || !header.startsWith("Bearer ")) {
            chain.doFilter(request, response);
            return;
        }

        String token = header.substring(7);

        try {
            Claims claims = jwtUtil.parse(token);

            // uid는 Number로 올 수 있음 → int로 안전 변환
            Long uid = (claims.get("uid") instanceof Number)
                    ? ((Number) claims.get("uid")).longValue()
                    : Long.parseLong(String.valueOf(claims.get("uid")));


            var auth = new UsernamePasswordAuthenticationToken(
                    uid,
                    null,
                    List.of(new SimpleGrantedAuthority("ROLE_USER"))
            );

            auth.setDetails(new WebAuthenticationDetailsSource().buildDetails(request));
            SecurityContextHolder.getContext().setAuthentication(auth);

            // 인증 설정 후 재확인
            Authentication setAuth = SecurityContextHolder.getContext().getAuthentication();

            chain.doFilter(request, response);
        } catch (ExpiredJwtException e) {
            write401(response, "ERROR_ACCESS_TOKEN_EXPIRED", e.getMessage());
        } catch (JwtException e) { // Malformed/Unsupported/Signature 등
            write401(response, "ERROR_ACCESS_TOKEN_INVALID", e.getMessage());
        } catch (Exception e) {
            write401(response, "ERROR_INTERNAL", e.getMessage());
        }
    }

    private void write401(HttpServletResponse res, String code, String msg) throws IOException {
        res.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
        res.setCharacterEncoding(StandardCharsets.UTF_8.name());
        res.setContentType(MediaType.APPLICATION_JSON_VALUE);
        String json = """
                {"error":"%s","message":"%s"}
                """.formatted(code, msg == null ? "" : msg.replace("\"","'"));
        res.getWriter().write(json);
    }
}