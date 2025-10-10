package com.stock.survive.util;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.ExpiredJwtException;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.JwtException;
import io.jsonwebtoken.SignatureAlgorithm;
import org.springframework.stereotype.Component;

import javax.crypto.SecretKey;
import java.time.Duration;
import java.util.Date;
import java.util.Map;

@Component
public class JWTUtil {

    private final SecretKey key;

    public JWTUtil(SecretKey key) {
        this.key = key;
        this.parser = Jwts.parserBuilder().setSigningKey(key).build();
    }

    private final io.jsonwebtoken.JwtParser parser;

    /** claims 포함, TTL(Duration)로 만료 설정해서 JWT 생성 */
    public String generateToken(Map<String, Object> claims, Duration ttl) {
        long now = System.currentTimeMillis();
        Date iat = new Date(now);
        Date exp = new Date(now + ttl.toMillis());

        return Jwts.builder()
                .setHeaderParam("typ", "JWT")
                .setClaims(claims)
                .setIssuedAt(iat)
                .setExpiration(exp)
                .signWith(key, SignatureAlgorithm.HS256)
                .compact();
    }

    /** 유효성 검증 + 클레임 반환 (실패 시 JwtException/ExpiredJwtException 등 발생) */
    public Claims parse(String token) throws JwtException, ExpiredJwtException {
        return parser.parseClaimsJws(token).getBody();
    }
}
