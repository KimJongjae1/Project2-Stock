package com.stock.survive.repository.tendency;

import com.stock.survive.entity.tendency.TendencyGameChart;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface GameChartsRepository extends JpaRepository<TendencyGameChart, Long> {

}
