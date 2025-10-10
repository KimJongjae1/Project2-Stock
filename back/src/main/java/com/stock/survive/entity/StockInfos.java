package com.stock.survive.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.time.LocalDate;
import java.time.LocalDateTime;

@Entity
@Getter
@AllArgsConstructor
@NoArgsConstructor
@Table(name = "stock_infos")
public class StockInfos {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long infoNo;

    @Column(nullable = false)
    private LocalDate date;

    @Column
    private Integer startPrice;

    @Column
    private Integer endPrice;

    @Column
    private Integer highPrice;

    @Column
    private Integer lowPrice;

    @Column
    private Long volume;

    @Column
    private Long marketCap;

    @Column
    private LocalDateTime createdAt;


    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "item_no", nullable = false)
    private StockItems stockItem;

}
