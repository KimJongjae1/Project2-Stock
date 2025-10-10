package com.stock.survive.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.util.HashSet;
import java.util.List;
import java.util.ArrayList;

import java.time.LocalDateTime;
import java.util.Set;

@Entity
@Builder
@AllArgsConstructor
@NoArgsConstructor
@Getter
@Table(name = "users")
public class User {

    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "user_no")
    private Long id;


    @Column(name = "social_email", length = 254, nullable = false, unique = true)
    private String socialEmail;

    @Builder.Default
    @Column(nullable = false)
    private boolean cancel = false;

    @Column(name = "nickname",length = 30, nullable = false)
    private String nickname;

    @OneToOne(mappedBy="user",
            cascade = CascadeType.ALL,
            orphanRemoval=true,
            fetch = FetchType.LAZY, optional=false)
    private Account account;

    @Column(name = "created_at", nullable = false)
    private LocalDateTime createdAt;

    @Column(name = "updated_at", nullable = false)
    private LocalDateTime updatedAt;

    @OneToMany(mappedBy = "user",
            cascade = CascadeType.REMOVE,
            orphanRemoval = true)
    @Builder.Default
    private List<OauthIdentity> identities = new ArrayList<>();

    @PrePersist
    void onCreate() {
        if (createdAt == null) createdAt = LocalDateTime.now();
        if (updatedAt == null) updatedAt = LocalDateTime.now();
        if (this.account == null) {
            this.account = Account.builder()
                    .user(this)
                    .totalReward(0)
                    .originalMoney(10_000_000L)
                    .cash(10_000_000L)
                    .haveStock(0L)
                    .build();
        }
    }

    @PreUpdate
    void onUpdate() {
        updatedAt = LocalDateTime.now();
    }

    public void changeNickname(String nickname) {
        this.nickname = nickname;
    }

    @ManyToMany(fetch = FetchType.LAZY)
    @JoinTable(
            name = "favorite_stocks",
            joinColumns = @JoinColumn(name = "user_no"),
            inverseJoinColumns = @JoinColumn(name = "item_no"),
            uniqueConstraints = @UniqueConstraint(
                    name = "uq_fav_user_item",
                    columnNames = {"user_no","item_no"}
            )
    )
    @Builder.Default
    private Set<StockItems> favorites = new HashSet<>();

    @PreRemove
    private void preRemove() {
        favorites.clear(); // 조인 테이블 행 정리시 사용
    }

}
