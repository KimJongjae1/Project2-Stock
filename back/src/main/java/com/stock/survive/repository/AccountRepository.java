package com.stock.survive.repository;

import com.stock.survive.entity.Account;
import jakarta.transaction.Transactional;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.Optional;

public interface AccountRepository extends JpaRepository<Account, Long> {
    @Query("select a from Account a join fetch a.user u where u.id = :userId")
    Optional<Account> findByUserId(@Param("userId") Long userId);
}
