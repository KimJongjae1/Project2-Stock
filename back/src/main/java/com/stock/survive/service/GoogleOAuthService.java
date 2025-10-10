package com.stock.survive.service;

import com.stock.survive.dto.OAuthUserInfo;

public interface GoogleOAuthService {

    OAuthUserInfo exchangeAndFetchUser(String code);


}
