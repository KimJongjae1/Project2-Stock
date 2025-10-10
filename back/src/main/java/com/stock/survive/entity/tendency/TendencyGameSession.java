package com.stock.survive.entity.tendency;

import com.stock.survive.entity.User;
import jakarta.persistence.CascadeType;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.FetchType;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.OneToMany;
import jakarta.persistence.Table;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Entity
@Table(name = "tendency_game_session")
public class TendencyGameSession {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_no", referencedColumnName = "user_no", nullable = false)
    private User user;
    
    @Column(name = "ticker", length = 20, nullable = false)
    private String ticker;
    
    @Column(name = "dataset_id", length = 50, nullable = false)
    private String datasetId;
    
    @Column(name = "company_alias", length = 50, nullable = false)
    private String companyAlias;
    
    @Column(name = "initial_cash", nullable = false)
    private Integer initialCash;
    
    @Column(name = "cash", nullable = false)
    private Integer cash;
    
    @Column(name = "stock_quantity", nullable = false)
    private Integer stockQuantity;
    
    @Column(name = "average_cost", nullable = false)
    private Integer averageCost;
    
    @Column(name = "realized_profit", nullable = false)
    private Long realizedProfit;
    
    @Column(name = "current_week", nullable = false)
    private Integer currentWeek;
    
    @Column(name = "max_week", nullable = false)
    private Integer maxWeek;
    
    @Enumerated(EnumType.STRING)
    @Column(name = "status", length = 20, nullable = false)
    private TendencyGameStatus status;
    
    @Column(name = "started_at", nullable = false)
    private LocalDateTime startedAt;
    
    @Column(name = "finished_at")
    private LocalDateTime finishedAt;
    
    @Column(name = "decision_elapsed_millis", nullable = false)
    private Long decisionElapsedMillis;
    
    @Column(name = "volatile_buy_count", nullable = false)
    private Integer volatileBuyCount;
    
    @Column(name = "volatile_sell_count", nullable = false)
    private Integer volatileSellCount;
    
    @Column(name = "sell_dominant_week_count", nullable = false)
    private Integer sellDominantWeekCount;
    
    @Builder.Default
    @OneToMany(mappedBy = "session", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<TendencyGameWeek> weeks = new ArrayList<>();
    
    @Builder.Default
    @OneToMany(mappedBy = "session", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<TendencyGameTrade> trades = new ArrayList<>();
}