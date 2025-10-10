package com.stock.survive.service;

import com.stock.survive.dto.MyPageDto;
import java.util.Set;

public interface MyPageService {
    MyPageDto getMyPage(Long userId);
    Set<Long> getFavoriteIdSet(Long userId);
    boolean isFavorite(Long userId, String ticker);
}