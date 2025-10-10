package com.stock.survive.config;

import jakarta.validation.constraints.NotBlank;
import lombok.Data;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Component;
import org.springframework.validation.annotation.Validated;

@Data
@Component
@Validated
@ConfigurationProperties(prefix = "oauth.google")
public class GoogleOAuthProperties {

    @NotBlank
    private String clientId;

    private String clientSecret;

    @NotBlank
    @Value("${oauth.google.redirect-uri}")
    private String redirectUri;

    // 구글 표준 엔드포인트(기본값)
    private String authorizeUri = "https://accounts.google.com/o/oauth2/v2/auth";
    private String tokenUri     = "https://oauth2.googleapis.com/token";
    private String userinfoUri  = "https://openidconnect.googleapis.com/v1/userinfo";

    // scope는 보통 이 셋이면 충분
    private String scope        = "openid email profile";
}
