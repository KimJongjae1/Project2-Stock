package com.stock.survive.dto;

import com.stock.survive.enumType.PlatformType;

public record OAuthUserInfo(
        PlatformType provider,
        String providerUserId,
        String email,
        String nickname,
        String profileImgUrl,
        boolean emailVerified
) {}
