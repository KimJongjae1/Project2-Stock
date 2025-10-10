package com.stock.survive.entity;

import jakarta.persistence.*;
import lombok.*;

import java.util.ArrayList;
import java.util.List;

@Entity
@Getter
@AllArgsConstructor
@NoArgsConstructor
@Table(name = "stock_items")
public class StockItems {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "item_no")
    private Long itemNo;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "item_category_no", nullable = false)
    private StockCategory category;

    @Column(name = "company_name", nullable = false, length = 100)
    private String companyName;

    @Column(name = "ticker", nullable = false, length = 6)
    private String ticker;

    @OneToMany(mappedBy = "stockItem", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<StockInfos> infos = new ArrayList<>();

    @OneToMany(mappedBy = "stockItems", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<TradeHistory> tradeHistories = new ArrayList<>();
}
