package com.stock.survive.dto;

import lombok.Builder;
import lombok.Data;

import java.util.List;
import java.util.stream.Collectors;
import java.util.stream.IntStream;

@Data
public class PageResponseDto<E> {

    private List<E> dtoList;
    private PageRequestDto pageRequestDto;
    private int totalCount;
    private boolean prev;
    private boolean next;
    private List<Integer> pageNumberList;
    private int prevPage;
    private int nextPage;
    private int totalPage;
    private int current;

    @Builder(builderMethodName = "withAll")
    public PageResponseDto(List<E> dtoList, PageRequestDto pageRequestDto, long total) {
        this.dtoList = dtoList;
        this.pageRequestDto = pageRequestDto;
        this.totalCount = (int) total;

        // 전체 페이지 수 계산
        int last = (int) Math.ceil(totalCount / (double) pageRequestDto.getSize());
        this.totalPage = last;

        // 모든 페이지 번호 생성 (1 ~ last)
        this.pageNumberList = IntStream.rangeClosed(1, last).boxed().collect(Collectors.toList());

        // 이전/다음 버튼 계산
        this.prev = pageRequestDto.getPage() > 1;
        this.next = pageRequestDto.getPage() < last;

        this.prevPage = prev ? pageRequestDto.getPage() - 1 : 0;
        this.nextPage = next ? pageRequestDto.getPage() + 1 : 0;

        this.current = pageRequestDto.getPage();
    }
}
