package com.stock.survive.repository;

import com.stock.survive.entity.GameResult;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface GameResultRepository extends JpaRepository<GameResult, Long> {
    
    Optional<GameResult> findTopByUserNoOrderByCreatedAtDesc(Long userNo);

    @Modifying(clearAutomatically = true, flushAutomatically = true)
    @Query("delete from GameResult gr where gr.userNo = :userId")
    int deleteByUserId(@Param("userId") Long userId);
}