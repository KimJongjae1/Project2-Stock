package com.stock.survive.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class TopNewsArticleDto {
    private String title;
    private String date;
    private String url;
    private int matchedKeywordsCount;
    private List<String> matchedKeywords;
}
