package com.stock.survive.service;

import com.stock.survive.entity.User;
import com.stock.survive.serviceImpl.TokenServiceImpl;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;

public interface TokenService {

    TokenServiceImpl.Pair issue(User u);

    void setRefreshCookie(HttpServletResponse res, String refresh);

    void clearRefreshCookie(HttpServletResponse res);

    String readRefreshCookie(HttpServletRequest req);

    String refreshFromCookie(HttpServletRequest req, HttpServletResponse res);

    void revokeFromCookie(HttpServletRequest req, HttpServletResponse res);
}
