package com.stock.survive.serviceImpl;

import com.stock.survive.dto.PageRequestDto;
import com.stock.survive.dto.PageResponseDto;
import com.stock.survive.dto.StockRealtimeDto;
import com.stock.survive.repository.StockRealtimeRepository;
import com.stock.survive.service.StockRealtimeService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.context.ApplicationEventPublisher;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
@Slf4j
public class StockRealtimeServiceImpl implements StockRealtimeService {

    private final StockRealtimeRepository stockRealtimeRepository;
    private final ApplicationEventPublisher eventPublisher;

    @Override
    public PageResponseDto<StockRealtimeDto> getList(PageRequestDto pageRequestDto) {
        Pageable pageable = PageRequest.of(
                pageRequestDto.getPage() - 1,
                pageRequestDto.getSize(),
                Sort.by("ticker").ascending()
        );

        Page<StockRealtimeDto> page = stockRealtimeRepository.findAllWithLatestInfo(pageable);

        return PageResponseDto.<StockRealtimeDto>withAll()
                .dtoList(page.getContent())
                .pageRequestDto(pageRequestDto)
                .total(page.getTotalElements())
                .build();
    }



}