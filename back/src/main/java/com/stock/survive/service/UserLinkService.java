package com.stock.survive.service;

import com.stock.survive.dto.OAuthUserInfo;
import com.stock.survive.entity.User;

public interface UserLinkService {

    User linkOrCreateByProvider(OAuthUserInfo info);
}
