package com.stock.survive.service;

import com.stock.survive.dto.UserSummaryDto;

public interface AuthService {
    UserSummaryDto me(Long userId);
}
