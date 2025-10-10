package com.stock.survive.service;

import com.stock.survive.dto.tendency.TendencyGameFinishRequest;
import com.stock.survive.dto.tendency.TendencyGameOrderRequest;
import com.stock.survive.dto.tendency.TendencyGameResponse;
import com.stock.survive.dto.tendency.TendencyGameStartRequest;
import com.stock.survive.dto.tendency.TendencyGameStateResponse;

public interface TendencyGameService {

    TendencyGameStateResponse start(Long userId, TendencyGameStartRequest request);

    TendencyGameStateResponse getState(Long userId, Long sessionId);

    TendencyGameStateResponse placeOrder(Long userId, Long sessionId, TendencyGameOrderRequest request);

    TendencyGameStateResponse proceedNextWeek(Long userId, Long sessionId);

    TendencyGameResponse finish(Long userId, TendencyGameFinishRequest request);
}
