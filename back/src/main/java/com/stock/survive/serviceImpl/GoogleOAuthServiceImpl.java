package com.stock.survive.serviceImpl;

import com.stock.survive.config.GoogleOAuthProperties;
import com.stock.survive.dto.OAuthUserInfo;
import com.stock.survive.enumType.PlatformType;
import com.stock.survive.service.GoogleOAuthService;
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
import java.nio.charset.StandardCharsets;
import java.util.UUID;

@Service
@RequiredArgsConstructor
@Log4j2
public class GoogleOAuthServiceImpl implements GoogleOAuthService {

    private final GoogleOAuthProperties props;
    private final RestTemplate restTemplate = new RestTemplate();

    private HttpSession session() {
        var attrs = (ServletRequestAttributes) RequestContextHolder.currentRequestAttributes();
        return attrs.getRequest().getSession(true);
    }

    /** 1) 인가 URL 생성 (state 저장) */
    public String buildAuthorizeUrl() {
        String state = UUID.randomUUID().toString();
        session().setAttribute("OAUTH2_GOOGLE_STATE", state);

        URI uri = UriComponentsBuilder.fromHttpUrl(props.getAuthorizeUri())
                .queryParam("client_id", props.getClientId())
                .queryParam("redirect_uri", props.getRedirectUri())
                .queryParam("response_type", "code")
                .queryParam("scope", props.getScope())
                .queryParam("state", state)
                // 선택 옵션들
                .queryParam("include_granted_scopes", "true")
                .queryParam("prompt", "select_account") // 계정 선택 유도
                .encode(StandardCharsets.UTF_8)
                .build().toUri();

        return uri.toString();
    }

    /** 2) state 검증 */
    public void verifyState(String state) {
        Object saved = session().getAttribute("OAUTH2_GOOGLE_STATE");
        session().removeAttribute("OAUTH2_GOOGLE_STATE");
        if (saved == null || !saved.equals(state)) {
            throw new IllegalArgumentException("INVALID_OAUTH_STATE");
        }
    }

    /** 3) 토큰 교환 + 유저 조회 → 공통 모델로 반환 */
    public OAuthUserInfo exchangeAndFetchUser(String code) {
        String accessToken = exchangeToken(code);
        GoogleUserResponse me = fetchUser(accessToken);

        return new OAuthUserInfo(
                PlatformType.GOOGLE,
                me.sub,                      // providerUserId
                me.email,                    // email(없을 수 있음)
                me.name,                     // nickname 대용으로 name
                me.picture,                  // 프로필 이미지
                Boolean.TRUE.equals(me.email_verified)
        );
    }

    private String exchangeToken(String code) {
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_FORM_URLENCODED);

        MultiValueMap<String,String> form = new LinkedMultiValueMap<>();
        form.add("grant_type", "authorization_code");
        form.add("client_id", props.getClientId());
        form.add("client_secret", props.getClientSecret());
        form.add("redirect_uri", props.getRedirectUri());
        form.add("code", code);

        ResponseEntity<GoogleTokenResponse> resp;
        try {
            resp = restTemplate.postForEntity(props.getTokenUri(),
                    new HttpEntity<>(form, headers),
                    GoogleTokenResponse.class);
        } catch (Exception e) {
            throw e;
        }

        return resp.getBody().access_token;
    }


    private GoogleUserResponse fetchUser(String accessToken) {
        HttpHeaders headers = new HttpHeaders();
        headers.setBearerAuth(accessToken);

        ResponseEntity<GoogleUserResponse> resp;
        try {
            resp = restTemplate.exchange(props.getUserinfoUri(),
                    HttpMethod.GET,
                    new HttpEntity<>(headers),
                    GoogleUserResponse.class);
        } catch (Exception e) {
            throw e;
        }

        return resp.getBody();
    }


    // --- 응답 모델 ---
    public static class GoogleTokenResponse {
        public String access_token;
        public Integer expires_in;
        public String token_type;
        public String scope;
        public String id_token; // 필요시 검증/파싱 가능
    }
    public static class GoogleUserResponse {
        public String sub;            // 고유 ID
        public String email;
        public Boolean email_verified;
        public String name;
        public String picture;
    }
}
