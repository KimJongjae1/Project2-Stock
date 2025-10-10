package com.stock.survive.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Entity
@Getter
@Builder
@AllArgsConstructor
@NoArgsConstructor
@Table(name = "stock_realtime")
public class StockRealtime {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long realtimeNo;

    @Column(length = 10, nullable = false)
    private String ticker;

    @Column(length = 100, nullable = false)
    private String companyName;

    @Column
    private Integer price;

    @Column
    private Double rate;

    @Column(name = "item_no")
    private Integer itemNo;

}
