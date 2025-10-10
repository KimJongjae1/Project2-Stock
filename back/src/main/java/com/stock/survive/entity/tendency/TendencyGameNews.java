package com.stock.survive.entity.tendency;

import jakarta.persistence.Column;
import jakarta.persistence.Embeddable;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.EqualsAndHashCode;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@Builder
@NoArgsConstructor
@AllArgsConstructor
@EqualsAndHashCode
@Embeddable
public class TendencyGameNews {

    @Column(name = "title", length = 200)
    private String title;

    @Column(name = "url", length = 400)
    private String url;

    @Column(name = "summary", length = 500)
    private String summary;
}
