package com.stock.survive.config;

import lombok.Data;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Component;

@Data
@Component
@ConfigurationProperties(prefix = "oauth.kakao")
public class KakaoOAuthProperties {
    private String clientId;
    private String clientSecret;
    
    @Value("${oauth.kakao.redirect-uri}")
    private String redirectUri;
    private String authorizeUri = "https://kauth.kakao.com/oauth/authorize";
    private String tokenUri     = "https://kauth.kakao.com/oauth/token";
    private String userinfoUri  = "https://kapi.kakao.com/v2/user/me";
}
