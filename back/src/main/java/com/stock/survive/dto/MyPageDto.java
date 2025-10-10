package com.stock.survive.dto;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.stock.survive.entity.GameResult;
import com.stock.survive.entity.TradeHistory;
import com.stock.survive.entity.User;
import lombok.*;

import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

@Getter @Setter
@Builder
@NoArgsConstructor @AllArgsConstructor
@JsonInclude(JsonInclude.Include.NON_NULL) // null 필드는 응답에서 숨김
public class MyPageDto {
    private Long userNo;
    private String socialEmail;
    private String nickname;
    private boolean cancel;
    private Integer totalReward;
    private Long cash;
    private String createdAt;
    private String avatarUrl;

    //관심종목
    private List<FavoriteItemDto> favorites;
    // 투자 성향 결과
    private Optional<GameResult> gameResult;
    // 모의투자 기록
    @Builder.Default
    private List<TradeHistoryDto> tradeHistory = List.of();

    private AccountSummaryDto account;

    /** 기본 정보만 채움 */
    public static MyPageDto ofBasic(User u, String avatarUrl) {
        return MyPageDto.builder()
                .userNo(u.getId())
                .socialEmail(u.getSocialEmail())
                .nickname(u.getNickname())
                .cancel(u.isCancel())
                .createdAt(u.getCreatedAt() != null
                        ? u.getCreatedAt().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME) : null)
                .avatarUrl(avatarUrl)
                .build(); 
    }

    /** 관심종목 리스트까지 채움 */
    public static MyPageDto ofWithFavorites(User u, String avatarUrl, List<FavoriteItemDto> favorites) {
        MyPageDto dto = ofBasic(u, avatarUrl);
        dto.setFavorites(favorites);
        return dto;
    }

    /** 게임 결과 데이터까지 채움 */
    public static MyPageDto ofWithFavAndGameResult(User u, String avatarUrl, List<FavoriteItemDto> favorites, Optional<GameResult> gameResult) {
        MyPageDto dto = ofBasic(u, avatarUrl);
        dto.setFavorites(favorites);
        dto.setGameResult(gameResult);
        return dto;
    }

    /** 마지막 거래 내역까지 채움 */
    public static MyPageDto ofFull(
            User u,
            String avatarUrl,
            List<FavoriteItemDto> favorites,
            Optional<GameResult> gameResult,
            List<TradeHistoryDto> tradeHistory,
            AccountSummaryDto account
    ) {
        MyPageDto dto = ofWithFavAndGameResult(u, avatarUrl, favorites, gameResult);
        dto.setTradeHistory(tradeHistory != null ? new ArrayList<>(tradeHistory) : new ArrayList<>());
        dto.setAccount(account);
        if (account != null) dto.setTotalReward(account.getTotalReward());
        return dto;
    }

    // 이거 다른 곳에서 쓰는 거랑 달라서 여기
    @Getter @Setter @AllArgsConstructor @NoArgsConstructor
    public static class FavoriteItemDto {
        private Long itemId;
        private String name;
        private String ticker;
    }

}
