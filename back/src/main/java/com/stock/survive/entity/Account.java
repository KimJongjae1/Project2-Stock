package com.stock.survive.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

@Entity
@Builder
@AllArgsConstructor
@NoArgsConstructor
@Getter
@Table(name = "accounts")
public class Account {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "account_no")
    private Long accountNo;

    @OneToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_no", nullable = false, unique = true,
            foreignKey = @ForeignKey(name = "fk_accounts_user"))
    private User user;

    @OneToMany(mappedBy = "account", cascade = CascadeType.ALL, orphanRemoval = true)
    @Builder.Default
    private List<TradeHistory> tradeHistories = new ArrayList<>();

    @Builder.Default
    @Column(name = "total_reward", nullable = false)
    private Integer totalReward = 0;

    @Builder.Default
    @Column(name = "original_money",nullable = false)
    private Long originalMoney = 10_000_000L;

    @Builder.Default
    @Column(name = "cash",nullable = false)
    private Long cash = 10_000_000L;

    @Builder.Default
    @Column(name = "haveStock",nullable = false)
    private Long haveStock=0L;

}
