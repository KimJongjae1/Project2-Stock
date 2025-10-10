package com.stock.survive.repository;

import com.stock.survive.entity.StockItems;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

public interface FavoriteRepository extends JpaRepository<StockItems, Long> {
    @Query("SELECT CASE WHEN COUNT(f) > 0 THEN true ELSE false END " +
            "FROM User u JOIN u.favorites f " +
            "WHERE u.id = :userId AND f.ticker = :ticker")
    boolean existsByUserIdAndTicker(@Param("userId") Long userId, @Param("ticker") String ticker);
}
