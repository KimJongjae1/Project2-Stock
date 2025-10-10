package com.stock.survive.config;

import com.stock.survive.security.handler.CustomAccessDeniedHandler;
import com.stock.survive.security.filter.JWTCheckFilter;
import com.stock.survive.security.RestAuthenticationEntryPoint;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.HttpMethod;
import org.springframework.security.config.Customizer;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.annotation.web.configurers.AbstractHttpConfigurer;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.CorsConfigurationSource;
import org.springframework.web.cors.UrlBasedCorsConfigurationSource;

import java.util.List;

@Configuration
@EnableWebSecurity
@RequiredArgsConstructor
public class SecurityConfig {

    private final JWTCheckFilter jwtCheckFilter;
    private final CustomAccessDeniedHandler accessDeniedHandler;
    private final RestAuthenticationEntryPoint authenticationEntryPoint;

    @Value("${app.cors.allowed-origins:http://localhost:5173}")
    private String allowedOrigins; // 콤마로 여러 개 가능

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
                .csrf(AbstractHttpConfigurer::disable)
                .cors(Customizer.withDefaults())
                .sessionManagement(s -> s.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
                .formLogin(AbstractHttpConfigurer::disable)
                .httpBasic(AbstractHttpConfigurer::disable)
                .authorizeHttpRequests(auth -> auth

                  
                    .requestMatchers(
                    "/oauth2/**",
                        "/login/oauth2/**",
                        "/users/auth/**",
                        "/api/users/auth/**"
                    ).permitAll()

                    // 기존 열어둔 것들
                    .requestMatchers(
                        "/api/users/logout",
                        "/error",
                        "/actuator/**",
                        "/api/actuator/**",
                        "/api/stock/**",
                        "/extract-keywords/**",
                        "/api/mypage/**",
                            "/api/trade/**",
                            "/api/influence/**"

                    ).permitAll()
                    // Tendency Game endpoints (public access)
                    .requestMatchers("/api/games/tendency/**").permitAll()
                    .requestMatchers(HttpMethod.POST, "/api/games").permitAll()
                    .requestMatchers(HttpMethod.OPTIONS, "/**").permitAll()
                    // 보호할 엔드포인트

                    .requestMatchers(HttpMethod.DELETE, "/api/users/me").authenticated()
                    .requestMatchers(HttpMethod.GET,    "/api/users/me").authenticated()
                    .anyRequest().authenticated()
                )
                .exceptionHandling(e -> e
                        .accessDeniedHandler(accessDeniedHandler)
                        .authenticationEntryPoint(authenticationEntryPoint)
                );

        http.addFilterBefore(jwtCheckFilter, UsernamePasswordAuthenticationFilter.class);
        return http.build();
    }

    @Bean
    public CorsConfigurationSource corsConfigurationSource() {
        CorsConfiguration cfg = new CorsConfiguration();
        cfg.setAllowedOrigins(List.of(allowedOrigins.split("\\s*,\\s*")));
        cfg.setAllowedMethods(List.of("GET","POST","PUT","PATCH","DELETE","OPTIONS"));
        cfg.setAllowedHeaders(List.of("Authorization","Content-Type","X-Requested-With"));
        cfg.setAllowCredentials(true); // 쿠키(리프레시) 사용 시 필수
        cfg.setMaxAge(3600L);

        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", cfg);
        return source;
    }
}
