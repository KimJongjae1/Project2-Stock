package com.stock.survive.entity.tendency;

import jakarta.persistence.CollectionTable;
import jakarta.persistence.Column;
import jakarta.persistence.ElementCollection;
import jakarta.persistence.Entity;
import jakarta.persistence.FetchType;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.Table;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.time.LocalDate;
import java.util.ArrayList;
import java.util.List;

@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Entity
@Table(name = "tendency_game_week")
public class TendencyGameWeek {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "session_id", nullable = false)
    private TendencyGameSession session;

    @Column(name = "week_index", nullable = false)
    private Integer weekIndex;

    @Column(name = "start_date", nullable = false)
    private LocalDate startDate;

    @Column(name = "end_date", nullable = false)
    private LocalDate endDate;

    @Column(name = "close_price", nullable = false)
    private Integer closePrice;

    @Column(name = "change_price", nullable = false)
    private Integer changePrice;

    @Column(name = "change_rate", nullable = false)
    private Double changeRate;

    @Builder.Default
    @ElementCollection
    @CollectionTable(name = "tendency_game_week_keyword", joinColumns = @JoinColumn(name = "week_id"))
    @Column(name = "keyword", length = 50)
    private List<String> keywords = new ArrayList<>();

    @Builder.Default
    @ElementCollection
    @CollectionTable(name = "tendency_game_week_news", joinColumns = @JoinColumn(name = "week_id"))
    private List<TendencyGameNews> news = new ArrayList<>();
}
