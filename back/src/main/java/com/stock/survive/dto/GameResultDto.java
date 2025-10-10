package com.stock.survive.dto;

import com.stock.survive.entity.GameResult;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.time.LocalDateTime;

@Data
@Builder
@AllArgsConstructor
@NoArgsConstructor
public class GameResultDto {
    private Long gameNo;
    private LocalDateTime createdAt;
    private Long userNo;
    private Integer tendencyI;
    private Integer tendencyE;
    private Integer tendencyS;
    private Integer tendencyN;
    private Integer tendencyF;
    private Integer tendencyT;
    private Integer tendencyJ;
    private Integer tendencyP;
    private String  tendencyResult;
    
    public static GameResultDto from(GameResult gr) {
        if (gr == null) return null;
        return GameResultDto.builder()
                .gameNo(gr.getGameNo())
                .userNo(gr.getUserNo())
                .createdAt(gr.getCreatedAt())
                .tendencyI(gr.getTendencyI())
                .tendencyE(gr.getTendencyE())
                .tendencyS(gr.getTendencyS())
                .tendencyN(gr.getTendencyN())
                .tendencyF(gr.getTendencyF())
                .tendencyT(gr.getTendencyT())
                .tendencyJ(gr.getTendencyJ())
                .tendencyP(gr.getTendencyP())
                .tendencyResult(gr.getTendencyResult())
                .build();
    }
}