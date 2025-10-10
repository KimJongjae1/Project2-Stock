package com.stock.survive.repository;

import com.stock.survive.entity.*;
import jakarta.transaction.Transactional;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;
import java.util.Optional;

public interface UserRepository extends JpaRepository<User, Long> {
    Optional<User> findBySocialEmail(String email);
    boolean existsByNickname(String nickname);

    // 헤더용 싹~ 다 빼고 identities만 넘겨서 프로필 이미지만 냄겨두기
    @Query("""
        select distinct u from User u
        left join fetch u.identities oi
        where u.id = :id
    """)
    Optional<User> findWithIdentitiesById(@org.springframework.data.repository.query.Param("id") Long id);

    // 마이페이지 상세: 즐겨찾기까지 필요할 때만 fetch join
    @Query("""
      select distinct u from User u
      left join fetch u.favorites
      where u.id = :id
    """)
    Optional<User> findWithFavoritesById(@org.springframework.data.repository.query.Param("id") Long id);

    // 메인에서 사용할 것 가볍게
    @Query("select f.itemNo from User u join u.favorites f where u.id = :userId")
    List<Long> findFavoriteItemIds(@org.springframework.data.repository.query.Param("userId") Long userId);

    @Transactional
    @Modifying
    @Query("UPDATE Account a SET a.cash = :cash, a.haveStock = :haveStock WHERE a.user.id = :userNo")
    void updateCashAndHaveStock(@Param("userNo") Long userNo, @Param("cash") Long cash, @Param("haveStock") Long haveStock);


}