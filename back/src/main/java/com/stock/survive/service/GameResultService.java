package com.stock.survive.service;

import com.stock.survive.dto.GameResultDto;
import com.stock.survive.dto.tendency.TendencyGameFinishRequest;
import com.stock.survive.dto.tendency.TendencyGameResponse;

public interface GameResultService {
    GameResultDto getLatestByUserNo(Long userNo);
    
    TendencyGameResponse finish(Long userId, TendencyGameFinishRequest request);
}