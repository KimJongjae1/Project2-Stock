package com.stock.survive.serviceImpl;

import com.stock.survive.config.KakaoOAuthProperties;
import com.stock.survive.dto.OAuthUserInfo;
import com.stock.survive.enumType.PlatformType;
import com.stock.survive.service.KakaoOAuthService;
import jakarta.servlet.http.HttpSession;
import lombok.RequiredArgsConstructor;
import lombok.extern.log4j.Log4j2;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.context.request.RequestContextHolder;
import org.springframework.web.context.request.ServletRequestAttributes;
import org.springframework.web.util.UriComponentsBuilder;

import java.net.URI;
import java.util.UUID;

@Service
@RequiredArgsConstructor
@Log4j2
public class KakaoOAuthServiceImpl implements KakaoOAuthService {


    private final KakaoOAuthProperties props;
    private final RestTemplate restTemplate = new RestTemplate();

    private HttpSession session() {
        var attrs = (ServletRequestAttributes) RequestContextHolder.currentRequestAttributes();
        return attrs.getRequest().getSession(true);
    }

    /** 1) 인가 URL 생성 (state를 세션에 저장) */
    public String buildAuthorizeUrl() {
        log.info("[KAKAO] clientId={}, redirect={}", props.getClientId(), props.getRedirectUri());
        String state = UUID.randomUUID().toString();
        session().setAttribute("OAUTH2_KAKAO_STATE", state);

        URI uri = UriComponentsBuilder.fromHttpUrl(props.getAuthorizeUri())
                .queryParam("client_id", props.getClientId())
                .queryParam("redirect_uri", props.getRedirectUri())
                .queryParam("response_type", "code")
                .queryParam("state", state)
                .build(true).toUri(); // true → 인코딩 유지
        return uri.toString();
    }

    /** 2) state 검증 */
    public void verifyState(String state) {
        Object saved = session().getAttribute("OAUTH2_KAKAO_STATE");
        session().removeAttribute("OAUTH2_KAKAO_STATE");
        if (saved == null || !saved.equals(state)) {
            throw new IllegalArgumentException("INVALID_OAUTH_STATE");
        }
    }

    /** 3) code로 토큰 교환 후 사용자 정보 조회 → OAuthUserInfo 반환 */
    public OAuthUserInfo exchangeAndFetchUser(String code) {
        String accessToken = exchangeToken(code);
        KakaoUserResponse user = fetchUser(accessToken);
        String providerUserId = String.valueOf(user.id);

        String email = null;
        String nickname = null;
        String profileImg = null;
        boolean emailVerified = false;

        if (user.kakao_account != null) {
            email = user.kakao_account.email;
            emailVerified = Boolean.TRUE.equals(user.kakao_account.is_email_verified) ||
                    Boolean.TRUE.equals(user.kakao_account.email_verified);
            if (user.kakao_account.profile != null) {
                nickname = user.kakao_account.profile.nickname;
                profileImg = user.kakao_account.profile.profile_image_url;
            }
        }

        return new OAuthUserInfo(
                PlatformType.KAKAO,
                providerUserId,
                email,
                nickname,
                profileImg,
                emailVerified
        );
    }

    // --- 내부: 토큰 교환 ---
    private String exchangeToken(String code) {
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_FORM_URLENCODED);

        MultiValueMap<String,String> form = new LinkedMultiValueMap<>();
        form.add("grant_type", "authorization_code");
        form.add("client_id", props.getClientId());
        if (props.getClientSecret() != null && !props.getClientSecret().isBlank()) {
            form.add("client_secret", props.getClientSecret());
        }
        form.add("redirect_uri", props.getRedirectUri());
        form.add("code", code);

        ResponseEntity<KakaoTokenResponse> resp = restTemplate.postForEntity(
                props.getTokenUri(),
                new HttpEntity<>(form, headers),
                KakaoTokenResponse.class
        );

        if (!resp.getStatusCode().is2xxSuccessful() || resp.getBody() == null || resp.getBody().access_token == null) {
            throw new IllegalStateException("KAKAO_TOKEN_EXCHANGE_FAILED");
        }
        return resp.getBody().access_token;
    }

    // --- 내부: 사용자 정보 조회 ---
    private KakaoUserResponse fetchUser(String accessToken) {
        HttpHeaders headers = new HttpHeaders();
        headers.setBearerAuth(accessToken);

        ResponseEntity<KakaoUserResponse> resp = restTemplate.exchange(
                props.getUserinfoUri(),
                HttpMethod.GET,
                new HttpEntity<>(headers),
                KakaoUserResponse.class
        );
        if (!resp.getStatusCode().is2xxSuccessful() || resp.getBody() == null) {
            throw new IllegalStateException("KAKAO_USERINFO_FETCH_FAILED");
        }
        return resp.getBody();
    }

    // --- Kakao 응답 모델 ---
    public static class KakaoTokenResponse {
        public String access_token;
    }
    public static class KakaoUserResponse {
        public long id;
        public KakaoAccount kakao_account;
    }
    public static class KakaoAccount {
        public String email;
        public Boolean is_email_verified; 
        public Boolean email_verified;
        public Profile profile;
    }
    public static class Profile {
        public String nickname;
        public String profile_image_url;
    }
}
