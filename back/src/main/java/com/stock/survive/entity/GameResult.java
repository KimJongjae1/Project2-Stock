package com.stock.survive.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import org.hibernate.annotations.CreationTimestamp;

import java.time.LocalDateTime;

@Entity
@Getter
@Builder
@AllArgsConstructor
@NoArgsConstructor
@Table(name = "game_results")
public class GameResult {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "game_no")
    private Long gameNo;

    @Column(name = "user_no", nullable = false)
    private Long userNo;

    @Column(name = "tendency_i", nullable = false)
    private Integer tendencyI;
    
    @Column(name = "tendency_e", nullable = false)
    private Integer tendencyE;
    
    @Column(name = "tendency_s", nullable = false)
    private Integer tendencyS;
    
    @Column(name = "tendency_n", nullable = false)
    private Integer tendencyN;
    
    @Column(name = "tendency_f", nullable = false)
    private Integer tendencyF;
    
    @Column(name = "tendency_t", nullable = false)
    private Integer tendencyT;
    
    @Column(name = "tendency_j", nullable = false)
    private Integer tendencyJ;
    
    @Column(name = "tendency_p", nullable = false)
    private Integer tendencyP;
    
    @Column(name = "tendency_result", nullable = false)
    private String tendencyResult;
    
    @CreationTimestamp
    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;
}