package com.stock.survive.service;

import com.stock.survive.dto.OAuthUserInfo;

public interface KakaoOAuthService {

    OAuthUserInfo exchangeAndFetchUser(String code);

}
