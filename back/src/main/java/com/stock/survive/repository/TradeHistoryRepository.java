package com.stock.survive.repository;

import com.stock.survive.dto.TradeHistoryDto;
import com.stock.survive.entity.TradeHistory;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface TradeHistoryRepository extends JpaRepository<TradeHistory, Long> {

    @Query("SELECT t FROM TradeHistory t WHERE t.user.id = :userNo AND t.stockItems.itemNo = :itemNo ORDER BY t.createdAt DESC")
    List<TradeHistory> findByUserAndStockItem(Long userNo, Long itemNo);

    @Query("""
    select new com.stock.survive.dto.TradeHistoryDto(
        si.itemNo, si.companyName,
        t.tradeType, t.price, t.volume, t.createdAt
    )
    from TradeHistory t
    join t.stockItems si
    where t.user.id = :userNo
    order by t.createdAt desc
  """)
    List<TradeHistoryDto> findAllByUser(Long userNo);
}
