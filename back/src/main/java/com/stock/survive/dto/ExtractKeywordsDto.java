package com.stock.survive.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;
import java.util.Map;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ExtractKeywordsDto {
    private String companyName;
    private String startDate;
    private String endDate;
    private Integer topKeywords;
    private boolean useAiFilter;
    private Map<String, Integer> keywords;
    private List<TopNewsArticleDto> topNewsArticles;
    private String aiAnalysis;
    private Map<String, Integer> dailyNewsCount;

}
