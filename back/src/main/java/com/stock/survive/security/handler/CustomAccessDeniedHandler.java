package com.stock.survive.security.handler;

import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.security.web.access.AccessDeniedHandler;
import org.springframework.stereotype.Component;

import java.nio.charset.StandardCharsets;
import java.util.Map;

@Component
public class CustomAccessDeniedHandler implements AccessDeniedHandler {

    private final ObjectMapper om = new ObjectMapper();

    @Override
    public void handle(HttpServletRequest req, HttpServletResponse res,
                       AccessDeniedException ex) {
        res.setStatus(HttpServletResponse.SC_FORBIDDEN); // 403
        res.setCharacterEncoding(StandardCharsets.UTF_8.name());
        res.setContentType("application/json");
        write(res, Map.of("error", "ACCESS_DENIED", "message", ex.getMessage()));
    }

    private void write(HttpServletResponse res, Object body) {
        try { om.writeValue(res.getOutputStream(), body);} catch (Exception ignored) {}
    }
}