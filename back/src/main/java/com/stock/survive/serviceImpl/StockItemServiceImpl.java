package com.stock.survive.serviceImpl;

import com.stock.survive.dto.FavoriteDto;
import com.stock.survive.dto.PageRequestDto;
import com.stock.survive.dto.PageResponseDto;
import com.stock.survive.dto.StockEndDayDto;
import com.stock.survive.repository.StockItemRepository;
import com.stock.survive.repository.UserRepository;
import com.stock.survive.service.StockItemService;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;

import java.time.LocalDate;

@Service
@RequiredArgsConstructor
public class StockItemServiceImpl implements StockItemService {

    private final StockItemRepository stockItemRepository;
    private final UserRepository userRepository;


    @Override
    public PageResponseDto<StockEndDayDto> getEndDayData(PageRequestDto pageRequestDto, LocalDate targetDate) {
        if (targetDate == null) {
            targetDate = stockItemRepository.findMaxDate();
        }

        Pageable pageable = PageRequest.of(pageRequestDto.getPage() - 1, pageRequestDto.getSize());

        // Repository에서 이미 DTO Page를 반환
        Page<StockEndDayDto> page = stockItemRepository.findEndOfDayLatest(targetDate, pageable);

        // 각 DTO에 rate 계산
        page.getContent().forEach(dto -> {
            if (dto.getStartPrice() != null && dto.getStartPrice() != 0 && dto.getEndPrice() != null) {
                double rate = ((dto.getEndPrice() - dto.getStartPrice()) * 100.0 / dto.getStartPrice());
                dto.setRate(Math.round(rate * 100.0) / 100.0); // 소수점 둘째자리까지
            }
        });

        return PageResponseDto.<StockEndDayDto>withAll()
                .dtoList(page.getContent())
                .pageRequestDto(PageRequestDto.builder()
                        .page(pageRequestDto.getPage())
                        .size(pageRequestDto.getSize())
                        .build())
                .total(page.getTotalElements())
                .build();
    }

    @Override
    public LocalDate getLatestDataDate() {
        return stockItemRepository.findMaxDate();
    }

    @Override
    public FavoriteDto getFavoriteStatus(Long userId, String ticker) {

        boolean isFavorite = userRepository.findWithFavoritesById(userId)
                .map(user -> user.getFavorites().stream()
                        .anyMatch(fav -> fav.getTicker().equals(ticker)))
                .orElse(false);

        return new FavoriteDto(isFavorite);
    }
}
