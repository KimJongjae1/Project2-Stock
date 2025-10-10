package com.stock.survive.security.refresh;

import java.time.Duration;

public interface RefreshTokenStore {
    String issue(Long userNo, Duration ttl);
    Long verify(String raw);
    void revoke(String raw);
}