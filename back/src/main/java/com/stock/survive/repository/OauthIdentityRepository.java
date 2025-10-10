package com.stock.survive.repository;
import com.stock.survive.entity.*;
import com.stock.survive.enumType.PlatformType;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface OauthIdentityRepository extends JpaRepository<OauthIdentity, Integer> {
    Optional<OauthIdentity> findByProviderAndProviderUserId(PlatformType provider, String providerUserId);
    Optional<OauthIdentity> findByProviderAndProviderEmail(PlatformType provider, String email);
}