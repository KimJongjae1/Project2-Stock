package com.stock.survive.entity;

import com.stock.survive.enumType.PlatformType;
import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDateTime;

@Entity
@Builder
@AllArgsConstructor
@NoArgsConstructor
@Getter
@Table(
        name = "platforms",
        uniqueConstraints = {
                @UniqueConstraint(name = "uq_user_provider", columnNames = {"user_no", "provider"})
        },
        indexes = {
                @Index(name = "idx_provider_sub", columnList = "provider, provider_user_id")
        }
)
public class OauthIdentity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "platform_no")
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "user_no", nullable = false,
            foreignKey = @ForeignKey(name = "fk_platforms_user"))
    private User user;

    @Enumerated(EnumType.STRING)
    @Column(name="provider",nullable = false)
    private PlatformType provider;

    @Column(name="provider_user_id",length = 191)
    private String providerUserId;

    @Column(name="provider_email",length = 254)
    private String providerEmail;

    @Column(name="profile_image_url", length = 512)
    private String profileImgUrl;

    @Builder.Default
    @Column(name="email_verified", nullable = false)
    private boolean emailVerified = false;

    @Column(name="connected_at", nullable = false)
    private LocalDateTime connectedAt;

    @PrePersist
    void onCreate() {
        if (connectedAt == null) connectedAt = LocalDateTime.now();
    }
}
