package com.stock.survive.serviceImpl;

import com.stock.survive.dto.OAuthUserInfo;
import com.stock.survive.entity.*;
import com.stock.survive.repository.*;
import com.stock.survive.service.UserLinkService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;

@Service
@RequiredArgsConstructor
public class UserLinkServiceImpl implements UserLinkService {

    private final UserRepository userRepo;
    private final OauthIdentityRepository oiRepo;

    @Transactional
    public User linkOrCreateByProvider(OAuthUserInfo info){
        // 1) OauthIdentity 우선 매칭
        OauthIdentity found = null;
        if (info.providerUserId() != null) {
            found = oiRepo.findByProviderAndProviderUserId(info.provider(), info.providerUserId()).orElse(null);
        }
        if (found == null && info.email() != null) {
            found = oiRepo.findByProviderAndProviderEmail(info.provider(), info.email()).orElse(null);
        }

        if (found != null) {
            // 기존 연결 업데이트(프로필/이메일 검증 등)
            // (필요시 setter 또는 빌더로 새 객체 저장)
            return found.getUser();
        }

        // 2) User 찾거나 생성 (email 기반)
        User user = (info.email() != null)
                ? userRepo.findBySocialEmail(info.email()).orElse(null)
                : null;

        if (user == null) {
            user = User.builder()
                    .socialEmail(info.email() != null ? info.email() : ("unknown+"+System.nanoTime()+"@placeholder.local"))
                    .nickname(info.nickname() != null ? info.nickname() : "user"+System.currentTimeMillis())
                    .build();
            // @PrePersist가 createdAt/updatedAt 채움
            user = userRepo.save(user);
        }

        // 3) OauthIdentity 생성
        OauthIdentity oi = OauthIdentity.builder()
                .user(user)
                .provider(info.provider())
                .providerUserId(info.providerUserId())
                .providerEmail(info.email())
                .profileImgUrl(info.profileImgUrl())
                .emailVerified(info.emailVerified())
                .connectedAt(LocalDateTime.now())
                .build();
        oiRepo.save(oi);

        return user;
    }
}
