package com.stock.survive.repository;

import com.stock.survive.dto.StockRealtimeDto;
import com.stock.survive.entity.StockRealtime;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface StockRealtimeRepository extends JpaRepository<StockRealtime, Long> {

    @Query("""
    SELECT new com.stock.survive.dto.StockRealtimeDto(
        si.ticker,
        si.companyName,
        inf.volume,
        inf.marketCap,
        sc.categoryName
    )
    FROM StockItems si
    JOIN si.category sc
    JOIN si.infos inf
    WHERE inf.date = (
        SELECT MAX(sinf.date) FROM StockInfos sinf WHERE sinf.stockItem.itemNo = si.itemNo
    )
    ORDER BY si.itemNo ASC
""")
    Page<StockRealtimeDto> findAllWithLatestInfo(Pageable pageable);
    

}
