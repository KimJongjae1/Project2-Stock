package com.stock.survive.serviceImpl;

import com.stock.survive.dto.GameResultDto;
import com.stock.survive.dto.tendency.TendencyGameFinishRequest;
import com.stock.survive.dto.tendency.TendencyGameResponse;
import com.stock.survive.entity.GameResult;
import com.stock.survive.repository.GameResultRepository;
import com.stock.survive.service.GameResultService;
import com.stock.survive.service.TendencyGameService;
import jakarta.transaction.Transactional;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.web.server.ResponseStatusException;

@Service
@RequiredArgsConstructor
public class GameResultServiceImpl implements GameResultService {
    
    private final GameResultRepository gameResultRepository;
    private final TendencyGameService tendencyGameService;
    
    @Override
    @Transactional(Transactional.TxType.SUPPORTS)
    public GameResultDto getLatestByUserNo(Long userNo) {
        GameResult gr = gameResultRepository
                .findTopByUserNoOrderByCreatedAtDesc(userNo)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "GAME_RESULT_NOT_FOUND"));
        
        return GameResultDto.from(gr);
    }
    
    @Override
    @Transactional
    public TendencyGameResponse finish(Long userId, TendencyGameFinishRequest request) {
        TendencyGameResponse response = tendencyGameService.finish(userId, request);
        
        GameResult gameResult = GameResult.builder()
                .userNo(userId)
                .tendencyI(response.tendencyI())
                .tendencyE(response.tendencyE())
                .tendencyS(response.tendencyS())
                .tendencyN(response.tendencyN())
                .tendencyF(response.tendencyF())
                .tendencyT(response.tendencyT())
                .tendencyJ(response.tendencyJ())
                .tendencyP(response.tendencyP())
                .tendencyResult(response.tendencyResult())
                .build();
        
        gameResultRepository.save(gameResult);
        
        return response;
    }
}