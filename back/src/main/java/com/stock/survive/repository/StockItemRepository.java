package com.stock.survive.repository;

import com.stock.survive.dto.StockEndDayDto;
import com.stock.survive.entity.StockItems;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDate;
import java.util.Optional;

@Repository
public interface StockItemRepository extends JpaRepository<StockItems, Long> {


    @Query("""
    SELECT new com.stock.survive.dto.StockEndDayDto(
        si.ticker,
        si.companyName,
        inf.startPrice,
        inf.endPrice,
        inf.volume,
        sc.categoryName,
        inf.marketCap
    )
    FROM StockItems si
    JOIN si.category sc
    JOIN si.infos inf
    WHERE inf.date = (
        SELECT MAX(sinf.date) 
        FROM StockInfos sinf 
        WHERE sinf.stockItem.itemNo = si.itemNo
          AND FUNCTION('DATE', sinf.date) = :targetDate
    )
    ORDER BY si.itemNo ASC
""")
    Page<StockEndDayDto> findEndOfDayLatest(@Param("targetDate") LocalDate targetDate, Pageable pageable);

    @Query("SELECT MAX(inf.date) FROM StockInfos inf")
    LocalDate findMaxDate();
    
    Optional<StockItems> findCompanyNameByTicker(String ticker);

    StockItems findByTicker(String ticker);
}
