package com.stock.survive.security.refresh;

import lombok.RequiredArgsConstructor;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Component;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.SecureRandom;
import java.time.Duration;
import java.util.HexFormat;

@Component
@RequiredArgsConstructor
public class RedisRefreshTokenStore implements RefreshTokenStore {

    private final StringRedisTemplate redis;
    private static final SecureRandom RNG = new SecureRandom();

    private static String sha256(String s) {
        try {
            MessageDigest d = MessageDigest.getInstance("SHA-256");
            return HexFormat.of().formatHex(d.digest(s.getBytes(StandardCharsets.UTF_8)));
        } catch (Exception e) { throw new RuntimeException(e); }
    }
    private static String key(String h) { return "rt:token:" + h; }

    @Override
    public String issue(Long userNo, Duration ttl) {
        byte[] b = new byte[64]; RNG.nextBytes(b);
        String raw = HexFormat.of().formatHex(b);
        String hash = sha256(raw);
        redis.opsForValue().set(key(hash), userNo.toString(), ttl);
        return raw; // 쿠키로 내려갈 실제 값
    }

    @Override
    public Long verify(String raw) {
        String v = redis.opsForValue().get(key(sha256(raw)));
        return v == null ? null : Long.valueOf(v);
    }

    @Override
    public void revoke(String raw) {
        redis.delete(key(sha256(raw)));
    }
}
