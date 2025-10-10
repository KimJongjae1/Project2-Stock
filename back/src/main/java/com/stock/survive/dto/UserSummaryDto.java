package com.stock.survive.dto;

import com.stock.survive.entity.User;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.time.format.DateTimeFormatter;

@Builder
@NoArgsConstructor
@AllArgsConstructor
@Getter
public class UserSummaryDto {
    private Long userNo;
    private String socialEmail;
    private String nickname;
    private boolean cancel;
    private Integer totalReward;
    private Long cash;
    private String createdAt;

    private String avatarUrl;

    public static UserSummaryDto of(User u) {
        return new UserSummaryDto(
                u.getId(), u.getSocialEmail(), u.getNickname(), u.isCancel(),
                u.getAccount().getTotalReward(), u.getAccount().getCash(),
                u.getCreatedAt() != null ? u.getCreatedAt().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME) : null,
                null // avatarUrl 기본값
        );
    }

    // ★ 필요하면 아바타까지 세팅하는 오버로드
    public static UserSummaryDto of(User u, String avatarUrl) {
        return new UserSummaryDto(
                u.getId(), u.getSocialEmail(), u.getNickname(), u.isCancel(),
                u.getAccount().getTotalReward(), u.getAccount().getCash(),
                u.getCreatedAt() != null ? u.getCreatedAt().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME) : null,
                avatarUrl
        );
    }
}


